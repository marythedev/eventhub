import stripe
from core.utils.stripe_utils import (create_and_confirm_payment,
                                     get_payment_intent)
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count, DecimalField, ExpressionWrapper, F
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from events.models import Event
from tickets.models import TicketInProcess

from .models import Order
from .utils import calculate_order_totals, reserve_tickets, save_tickets

STRIPE_PUBLIC_KEY = settings.STRIPE_PUBLIC_KEY

@login_required
def checkout(request, event_id):    # pylint: disable=too-many-return-statements
    """
    Handle payment for ticket purchases.

    Workflow:
        - Load selected tickets from session or restore previously reserved (TicketInProcess) tickets (if any).
        - Compute totals (subtotal, service fee, tax, total).
        - If total = 0 (free tickets only): skip Stripe payment and auto-complete order.
        - If total > 0 (paid only or paid/free tickets):
            - Creates and confirms a Stripe PaymentIntent.
            - If payment succeeds:
                - Saves the order and creates tickets.
            - If payment requires action:
                - Store the client secret in session and redirect to action-required page.
            - If payment fails:
                - Save failed order and release all tickets in process for this order.
        - Redirects to success, failure or action-required page depending on payment outcome.

    Args:
        request (HttpRequest)
        event_id (int): ID of the event, which tickets are being purchased.
    """

    event = get_object_or_404(Event, id=event_id)

    if not event.organizer.stripe_account.stripe_account_ready:
        raise Http404("Event not found")

    checkout_tickets = None
    selected_tickets = request.session.pop("selected_tickets", None)
    if selected_tickets:
        # delete previously reserved tickets
        TicketInProcess.objects.filter(reserver=request.user, order__isnull=True, price_zone__event=event).delete()

        # reserve newly selected
        checkout_tickets = reserve_tickets(tickets=selected_tickets, reserver=request.user)
    else:
        # get previously reserved (TicketInProcess) tickets (if any)
        checkout_tickets = TicketInProcess.objects.filter(
            reserver=request.user,
            order__isnull=True,
            price_zone__event=event
        )

    if not checkout_tickets:
        return redirect('events:view_event', event_id=event.id)

    subtotal, service_fee, tax, total = calculate_order_totals(checkout_tickets)

    if total == 0:
        order = Order.objects.create(
            status="succeeded",
            stripePaymentId=None,
            acquirer=request.user,
            subtotal=subtotal,
            tax=tax,
            service_fee=service_fee,
            total=total
        )
        save_tickets(tickets=checkout_tickets, order=order)
        return redirect("checkout:success", event_id=event.id, order_number=order.number)

    if request.method == "POST":
        payment_method_id = request.POST.get("payment_method_id")

        try:
            confirmed_intent = create_and_confirm_payment(total, payment_method_id, request.user.email)

            # save order to db
            order = Order.objects.create(
                status = confirmed_intent.status,
                stripePaymentId = confirmed_intent.id,
                acquirer = request.user,
                subtotal = subtotal,
                tax = tax,
                service_fee = service_fee,
                total = total
            )

            if confirmed_intent.status == "succeeded":
                save_tickets(tickets=checkout_tickets, order=order)
                return redirect("checkout:success", event_id=event.id, order_number=order.number)

            # add order to tickets in process
            for ticket in checkout_tickets:
                ticket.order = order
                ticket.save()

            if confirmed_intent.status == "requires_action":
                request.session['payment_intent_client_secret'] = confirmed_intent.client_secret
                return redirect('checkout:action_required', event_id=event.id, order_number=order.number)

            # release tickets in process
            checkout_tickets.delete()
            return redirect("checkout:fail", event_id=event.id, order_number=order.number)

        except stripe.StripeError as e:
            checkout_tickets.delete()

            # payment fails
            if hasattr(e.error, "payment_intent") and e.error.payment_intent:
                # save failed order to db
                order = Order.objects.create(
                    status = e.error.payment_intent.status,
                    stripePaymentId = e.error.payment_intent.id,
                    acquirer = request.user,
                    subtotal = subtotal,
                    tax = tax,
                    service_fee = service_fee,
                    total = total
                )
                request.session["checkout_fail_message"] = e.error.payment_intent.last_payment_error.message
                return redirect("checkout:fail", event_id=event.id, order_number=order.number)

    return render(request, 'checkout/checkout.html', {
        'event': event,
        'selected_tickets': checkout_tickets.values('price_zone__name', 'price_zone__price').annotate(
            quantity=Count('id')
        ).annotate(total=ExpressionWrapper(F('quantity') * F('price_zone__price'), output_field=DecimalField())),
        'subtotal': subtotal,
        'service_fee': service_fee,
        'tax': tax,
        'total': total,
        'STRIPE_PUBLIC_KEY': STRIPE_PUBLIC_KEY
    })


@login_required
def action_required(request, event_id, order_number):
    """
    Handle additional payment authentication.
    Authentication for PaymentIntents in 'requires_action' state.
    
    Args:
        request (HttpRequest)
        event_id (int): ID of the event for which purchase is made.
        order_number (str): Unique number of the order associated with payment intent.

    GET:
        Renders authentication page using Stripe.

    POST:
        Updates order status and redirects to success or failure pages depending on payment outcome.
    """

    payment_client_secret = request.session.get("payment_intent_client_secret")

    if not payment_client_secret:
        return redirect("checkout:checkout", event_id)

    event = get_object_or_404(Event, id=event_id)
    order = get_object_or_404(Order, number=order_number, acquirer=request.user)

    if request.method == "POST":
        payment_intent_id = order.stripePaymentId
        checkout_tickets = TicketInProcess.objects.filter(reserver=request.user, order=order, price_zone__event=event)

        try:
            payment_intent = get_payment_intent(payment_intent_id)
            order.status = payment_intent.status
            order.save()

            request.session.pop("payment_intent_client_secret", None)

            if payment_intent.status != "succeeded":
                checkout_tickets.delete()
                request.session["checkout_fail_message"] = "Payment authentication failed. Please try again."
                return redirect("checkout:fail", event_id=event.id, order_number=order.number)

            return redirect("checkout:success", event_id=event.id, order_number=order.number)

        except stripe.StripeError:
            checkout_tickets.delete()
            request.session["checkout_fail_message"] = (
                "An error occurred while processing your payment. Please try again."
            )
            return redirect("checkout:fail", event_id=event.id, order_number=order.number)

    return render(request, "checkout/action_required.html", {
        "event": event,
        "order": order,
        "STRIPE_PUBLIC_KEY": STRIPE_PUBLIC_KEY,
        "payment_intent_client_secret": payment_client_secret
    })


@login_required
def success(request, event_id, order_number):
    """
    Display the payment success page.

    Redirects to the event page or payment fail page if the check fails.
    Otherwise displays payment success page.

    Validates:
        - order_number: belongs to the logged in user
        - payment succeeded: otherwise redirects to payment fail page

    Args:
        event_id (int): ID of the event for which the order was made.
        order_number (str): Unique number of the order that was made by the user and is successful.
    """

    event = get_object_or_404(Event, id=event_id)
    order = get_object_or_404(Order, number=order_number, acquirer=request.user)

    if order.status != 'succeeded':
        return redirect('checkout:fail', event_id=event.id, order_number=order.number)

    purchased_tickets = (
        order.tickets
        .values("price_zone__name")
        .annotate(quantity=Count("id"))
    )

    return render(request, 'checkout/success.html', {
        'event': event, 
        'order': order,
        'purchased_tickets': purchased_tickets
    })


@login_required
def fail(request, event_id, order_number):
    """
    Display the payment fail page.

    Redirects to the event page or payment success page if the check approves.
    Otherwise displays payment fail page.

    Validates:
        - order_number: belongs to the logged in user
        - payment did not succeed: otherwise redirects to payment success page

    Args:
        event_id (int): ID of the event for which the order was made.
        order_number (str): Unique number of the order that was made by the user and has failed.
    """

    event = get_object_or_404(Event, id=event_id)
    order = get_object_or_404(Order, number=order_number)

    # users cannot see orders that are not their own
    if order.acquirer != request.user:
        return redirect("events:view_event", event_id=event.id)

    checkout_fail_message = request.session.pop("checkout_fail_message", None)

    if order.status == 'succeeded':
        return redirect('checkout:success', event_id=event.id, order_number=order.number)
    return render(request, 'checkout/fail.html', { "message": checkout_fail_message })
