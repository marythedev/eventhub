import stripe
from django.conf import settings

STRIPE_PUBLIC_KEY = settings.STRIPE_PUBLIC_KEY
STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY
stripe.api_key = STRIPE_SECRET_KEY

def get_stripe_account(user):
    """
    Get user's Stripe account and update account readiness status (stripe_account.stripe_account_ready).
        Account is ready if all details are submitted and no verification is pending

    Args:
        user (Profile): The user whose Stripe account is retrieved.

    Returns:
        stripe.Account: The Stripe account object.
    """

    account = stripe.Account.retrieve(user.stripe_account.stripe_account_id)

    # keep user's account status up-to-date
    if (account.details_submitted
        and not account.requirements.currently_due
        and not account.requirements.pending_verification
        and not account.requirements.disabled_reason):
        user.stripe_account.stripe_account_ready = True
    else:
        user.stripe_account.stripe_account_ready = False
    user.stripe_account.save(update_fields=['stripe_account_ready'])

    return account

def create_stripe_account(user):
    """
    Create a new Stripe Express account for a user and save its ID in the database.

    Args:
        user (Profile): The user for whom to create the account.

    Returns:
        stripe.Account: The newly created Stripe account object.
    """

    account = stripe.Account.create(type="express")
    user.stripe_account.stripe_account_id = account.id
    user.stripe_account.save(update_fields=['stripe_account_id'])
    return account

def get_stripe_account_link(user):
    """
    Generate a Stripe account link for onboarding or login (account management).

    Returns an onboarding URL if stripe onboarding is incomplete and no details were submitted.
    Otherwise, returns a login URL to manage account.

    Args:
        user (Profile): The user who is the owner of the Stripe account.

    Returns:
        tuple: (onboarding_url, login_url) where one of them is None.
    """

    if not user.stripe_account.stripe_account_id:
        account = create_stripe_account(user)
    else:
        account = get_stripe_account(user)

    # account has onboarded (account manage link)
    if account.details_submitted:
        login_link = stripe.Account.create_login_link(user.stripe_account.stripe_account_id)
        return None, login_link.url

    # account has not onboarded (account onboarding link)
    account_link = stripe.AccountLink.create(
        account=user.stripe_account.stripe_account_id,
        refresh_url=f"{settings.DOMAIN_URL}/account/#bank",
        return_url=f"{settings.DOMAIN_URL}/account/#bank",
        type="account_onboarding"
    )
    return account_link.url, None

def delete_stripe_account(user):
    """
    Delete a user's Stripe account and reset stripe information in the database.

    Args:
        user (Profile): The user whose account is being deleted.
    """

    if user.stripe_account.stripe_account_id:
        stripe.Account.delete(user.stripe_account.stripe_account_id)
        user.stripe_account.stripe_account_id = None
        user.stripe_account.stripe_account_ready = False
        user.stripe_account.save()

def create_and_confirm_payment(
    customer_email,
    customer_payment_method_id,
    event_organizer_stripe,
    subtotal,
    service_fee):
    """
    Payment from customer to event organizer via Stripe.
    Create and confirm a Stripe PaymentIntent.

    Args:
        customer_email (str): Email of the customer for receipt.
        customer_payment_method_id (str): Customer's payment method ID (i.e. credit card) provided through the frontend.
        event_organizer_stripe (StripeAccount): StripeAccount object containing event organizer's Stripe account ID.
        subtotal (float): Money portion for the tickets including tax (no service fee).
        service_fee (float): Money portion for service fee.

    Returns:
        stripe.PaymentIntent: Confirmed PaymentIntent object.
    """

    stripe.api_key = STRIPE_SECRET_KEY
    total = subtotal + service_fee
    payment_intent = stripe.PaymentIntent.create(
        amount=int(total * 100),
        currency="usd",
        payment_method=customer_payment_method_id,
        receipt_email=customer_email,
        automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
        transfer_data={
            "destination": event_organizer_stripe.stripe_account_id,
        },
        application_fee_amount=int(service_fee * 100)
    )

    # payment confirmation
    confirmed_intent = stripe.PaymentIntent.confirm(
        payment_intent.id,
        payment_method=customer_payment_method_id
    )
    return confirmed_intent

def get_payment_intent(payment_intent_id):
    """Retrieve Stripe PaymentIntent by id."""
    return stripe.PaymentIntent.retrieve(payment_intent_id)
