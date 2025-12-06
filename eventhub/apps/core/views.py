from core.utils.utils import get_upcoming_user_events, paginate_queryset
from django.shortcuts import render

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
