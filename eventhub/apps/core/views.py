from core.utils.utils import get_upcoming_user_events, paginate_queryset
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from .forms import ContactInquiryValidator
from .models import ContactInquiry
from .utils.event_recommendation_utils import get_recommended_events


def home(request):
    """
    Display landing page or user's home page with personalized data.

    If the user is authenticated:
        - Displays the top 3 upcoming events the user has purchased tickets for, ordered by the closest date.
        - Displays recommended events based on the user's purchase history, location, and preferences.
          - Events are paginated based on the 'show' query parameter, which specifies how many events fit in one row.
          - 'max_recommend_results' (default 12) defines the maximum number of recommended events to show.

    If the user is not authenticated:
        - Renders landing page.
    """

    user = request.user

    if not user.is_authenticated:
        return render(request, "core/home.html")

    upcoming_events = get_upcoming_user_events(user)
    upcoming_more = len(upcoming_events) - 3
    upcoming_events = upcoming_events[:3]
    recommended_events = get_recommended_events(user, max_recommend_results=12)

    events_per_row = request.GET.get('show', 4)
    events_per_row = max(int(events_per_row), 2)

    paginated_events, query = paginate_queryset(
        queryset=recommended_events,
        request=request,
        display_per_page=events_per_row
    )

    return render(request, "core/home.html", {
        "recommended_events": paginated_events,
        "upcoming_events": upcoming_events,
        "upcoming_more": upcoming_more,
        'query': query,
    })


def contact(request):
    """
    Handle contact inquiry requests.
    
    GET:
        Serve contact form page.
            - if user is authenticated, pre-fill user details
            - if user is not authenticated, display an empty contact form

    POST:
        Validate contact form input.

        On Validation success:
            - Create contact inquiry object (ContactInquiry) with the validated provided details.
            - Send email notification to app's team.
            - Redirect to contact form with success message.

        On Validation fail:
            - Return contact form with errors.
    """

    if request.method == "POST":
        form = ContactInquiryValidator(request.POST)

        if form.is_valid():
            inquiry = ContactInquiry.objects.create(
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message']
            )

            try:
                send_mail(
                    subject="EventHub: Contact Us Inquiry",
                    message=(
                        f"{inquiry.message}\n\n"
                        f"Name: {inquiry.full_name}\n"
                        f"Email: {inquiry.email}"
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_HOST_USER]
                )
                messages.success(request, "Thank you, we have received your message.")
            except Exception:       # pylint: disable=broad-exception-caught
                messages.error(request, "Something went wrong, please try again.")
            return redirect("contact")
    else:
        if request.user.is_authenticated:
            form = ContactInquiryValidator(initial={
                "full_name": request.user.full_name,
                "email": request.user.email
            })
        else:
            form = ContactInquiryValidator()

    return render(request, 'core/contact.html', { "form": form })


def terms_and_conditions(request):
    """Display the page with platform's terms and conditions."""
    return render(request, 'core/terms-and-conditions.html')
