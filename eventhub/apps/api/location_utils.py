import os
from math import asin, cos, radians, sin, sqrt

import requests
from django.core.exceptions import ValidationError


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on the Earth.
    
    Args:
        lat1, lon1: Latitude and longitude of the first point.
        lat2, lon2: Latitude and longitude of the second point.

    Returns:
        Distance in kilometers
    """

    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * 6371 * asin(sqrt(a))

def validate_location(location):
    """
    Validate and normalize a location string using OpenStreetMap API.

    Behavior:
        - Fetch OpenStreetMap with the provided location string.
        - Ensure at least one result exists.
        - Normalize location input with the display_name returned by OpenStreetMap.

    Args:
        location (str): Location to be validated.

    Raises:
        ValidationError when:
            - Location is not valid (not found).
            - OpenStreetMap fetch fails.

    Returns:
        location (str): Validated and normalized location string.
    """

    try:
        # fetch openstreetmap to check if location exists
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': location, 'format': 'json'},
            headers={
                'User-Agent': f'Eventhub/{os.getenv("APP_VERSION", "1.0")}',
                'Accept-Language': 'en'
            },
            timeout=7
        )
        data = response.json()

        if len(data) == 0:
            raise ValidationError("Location not found. Please enter a valid place.")

        # transform location to full display name for consistent location format
        location = data[0]['display_name']
        latitude = float(data[0]['lat'])
        longitude = float(data[0]['lon'])

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError("Failed to validate location. Try again later.") from e

    return location, latitude, longitude
