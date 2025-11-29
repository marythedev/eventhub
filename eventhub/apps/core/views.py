from django.shortcuts import render

from .utils import get_recommended_events, get_upcoming_user_events


def home(request):
    """
    Display landing page or user's home page with personalized data.

    If the user is authenticated:
        - Fetches upcoming events the user has purchased tickets for.
        - Fetches recommended events based on user's purchase history, location and preferences.

    If the user is not authenticated:
        - Renders landing page.
    """

    user = request.user

    if not user.is_authenticated:
        return render(request, "core/home.html")

    upcoming_events = get_upcoming_user_events(user)
    recommended_events = get_recommended_events(user)

    return render(request, "core/home.html", {
        "upcoming_events": upcoming_events,
        "recommended_events": recommended_events
    })
