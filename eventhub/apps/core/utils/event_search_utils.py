from django.db.models import Q


def event_search_filter(events, query):
    """
    Filter events by search query against name, location or category (case-insensitive).

    Args:
        events: initial QuerySet of Event to filter
        query: GET parameters

    Returns:
        Filtered Event QuerySet.
    """

    search_query = query.get('search', '').strip()
    if search_query:
        events = events.filter(
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(category__icontains=search_query)
        ).distinct()
    return events

def event_search_name_filter(events, query):
    """
    Filter events by search query against name (case-insensitive).

    Args:
        events: initial QuerySet of Event to filter
        query: GET parameters

    Returns:
        Filtered Event QuerySet.
    """

    search_query = query.get('search', '').strip()
    if search_query:
        events = events.filter(
            Q(name__icontains=search_query)
        ).distinct()
    return events
