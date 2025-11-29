from collections import Counter

from api.utils import get_unique_events_from_orders, haversine
from django.db.models import (Case, Count, F, IntegerField, Max, Min, Q,
                              Subquery, Value, When)
from django.utils import timezone
from events.models import Event


def _get_order_insights(user):
    """
    Create insights based on user's previous orders.

    Insights:
    - Minimum and maximum price of purchased events.
    - Top 3 categories of purchased events.

    Args:
        user (Profile): User whose orders are evaluated.

    Returns:
        insights (dict): 'min_price', 'max_price', 'categories'.
    """

    insights = {
        "min_price": 0,
        "max_price": 0,
        "categories": []
    }

    purchased_events = get_unique_events_from_orders(user)

    if purchased_events.exists():
        # price range from user purchased events
        prices = purchased_events.aggregate(
            min_price=Min("price_zones__price"),
            max_price=Max("price_zones__price")
        )

        insights["min_price"] = prices["min_price"]
        insights["max_price"] = prices["max_price"]

        # top 3 categories from user purchased events
        categories = list(purchased_events.values_list("category", flat=True))
        category_counter = Counter(categories)
        insights["categories"] = [c for c, _ in category_counter.most_common(3)]

    return insights

def _make_event_pool(max_event_pool):
    """
    Make a set of 'max_event_pool' number events.
        - Events must be upcoming (date >= now).
        - Event organizer has setup Stripe payouts to receive payments from ticket purchases.

    Args:
        max_event_pool (int): Maximum number of events to include in the pool.

    Returns:
        QuerySet: A queryset of 'max_event_pool' Event objects.
    """

    event_pool = Event.objects.filter(
        date__gte=timezone.now(),
        organizer__stripe_account__stripe_account_ready=True
    ).values_list("id", flat=True)[:max_event_pool]

    events = Event.objects.filter(id__in=Subquery(event_pool))

    return events

def _score_category(events, user_top_categories):
    """
    Annotate events with 'category_score'.
        - 30 points if event category is in top 3 user categories.

    Args:
        events: Event QuerySet to score.
        user_top_categories (list): Top 3 categories.

    Returns:
        QuerySet: Events annotated with 'category_score'.
    """

    events = events.annotate(
        category_score=Case(
            When(category__in=user_top_categories, then=Value(30)),
            default=Value(0),
            output_field=IntegerField()
        )
    )

    return events

def _score_location(events, user):
    """
    Annotate events with 'location_score'.
        - 40 points if event's location is within 25km of user's location.
    If no user location set, location score is 0 (gets ignored).

    Args:
        events: Event QuerySet to score.
        user (Profile): The user whose location is used for scoring.

    Returns:
        QuerySet: Events annotated with 'location_score'.
    """

    if user.location:
        events_in_radius_ids = []
        for e in events:
            distance = haversine(user.location_lat, user.location_lon, e.location_lat, e.location_lon)
            if distance <= 25:
                events_in_radius_ids.append(e.id)

        events = events.annotate(
            location_score=Case(
                When(id__in=events_in_radius_ids, then=Value(40)),
                default=Value(0),
                output_field=IntegerField()
            )
        )
    else:
        events = events.annotate(
            location_score=Value(0, output_field=IntegerField())
        )

    return events

def _score_price(events, user_max_price, user_min_price):
    """
    Annotate events with 'price_score' based on whether event's price is within user's previous purchase price range.
        - 20 points if event price matches both 'user_max_price' and'user_min_price'.
        - 10 points if event price matches 'user_max_price'.
    If user has no previous purchases, price score is 0 (gets ignored).

    Args:
        events: Event QuerySet to score.
        user_max_price (float): User's maximum purchased event price.
        user_min_price (float): User's minimum purchased event price.

    Returns:
        QuerySet: Events annotated with 'price_score'.
    """

    if user_max_price > 0:
        events = events.annotate(
            max_price=Max("price_zones__price"),
            min_price=Min("price_zones__price")
        )

        events = events.annotate(
            price_score=Case(
                When(max_price__lte=user_max_price, min_price__gte=user_min_price, then=Value(20)),
                When(max_price__lte=user_max_price, then=Value(10)),
                default=Value(0),
                output_field=IntegerField()
            )
        )
    else:
        events = events.annotate(
            price_score=Value(0, output_field=IntegerField())
        )
    return events

def _purchased_penalty(events, user):
    """
    Purchased events are not prioritized.
    Remove 1000 points from events that the user has already purchased tickets for.

    Args:
        events: Event QuerySet to score.
        user (Profile): The user whose orders/tickets are reviewed.

    Returns:
        QuerySet: Events annotated with 'purchased_penalty'.
    """

    purchased_ids = get_unique_events_from_orders(user).values_list("id", flat=True)

    events = events.annotate(
        purchased_penalty=Case(
            When(id__in=purchased_ids, then=Value(-1000)),
            default=Value(0),
            output_field=IntegerField()
        )
    )

    return events

def get_recommended_events(user, max_event_pool=500, max_recommend_results=10):
    """
    Get personalized recommended events for a user.

    Events are scored by:
    - Category match
    - Location closeness
    - Price range match based on previous orders
    - If user already has tickets to this event

    Args:
        user (User): The user for whom recommendations are created.
        max_event_pool (int): Maximum number of events to consider.
        max_recommend_results (int): Maximum number of recommended events to return.

    Returns:
        QuerySet: Top recommended events ordered by relevance score and date.
    """

    insights = _get_order_insights(user)

    events = _make_event_pool(max_event_pool)
    events = _score_category(events, insights["categories"])
    events = _score_location(events, user)
    events = _score_price(events, insights["max_price"], insights["min_price"])
    events = _purchased_penalty(events, user)

    events = events.annotate(
        relevance_score=(
            F("category_score") + F("location_score") + F("price_score") + F("purchased_penalty")
        )
    ).order_by("-relevance_score", "date")

    return events[:max_recommend_results]

def get_upcoming_user_events(user):
    """
    Get upcoming events that user has purchased tickets for.
    Annotates each event with the number of tickets the user owns for that event.

    Args:
        user (User): User whose upcoming events are being fetched.

    Returns:
        QuerySet: Upcoming events ordered by date with 'tickets_owned' annotation.
    """

    upcoming_events = get_unique_events_from_orders(user).filter(
        date__gte=timezone.now()
    )

    # owned ticket number annotation
    upcoming_events = upcoming_events.annotate(
        tickets_owned=Count(
            'price_zones__tickets',
            filter=Q(price_zones__tickets__order__acquirer=user)
        )
    ).order_by('date')

    return upcoming_events
