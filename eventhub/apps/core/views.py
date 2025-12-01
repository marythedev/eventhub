from api.event_recommendation_utils import get_recommended_events
from api.utils import get_upcoming_user_events
from django.core.paginator import Paginator
from django.shortcuts import render


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

    upcoming_events = get_upcoming_user_events(user)[:3]
    recommended_events = get_recommended_events(user, max_recommend_results=12)

    events_per_row = request.GET.get('show', 4)
    events_per_row = max(int(events_per_row), 2)

    paginator = Paginator(recommended_events, events_per_row)
    page_number = request.GET.get('page')
    paginated_events = paginator.get_page(page_number)

    # remove page parameter
    query = request.GET.copy()
    query.pop('page', None)

    return render(request, "core/home.html", {
        "upcoming_events": upcoming_events,
        "recommended_events": paginated_events,
        'query': query
    })
