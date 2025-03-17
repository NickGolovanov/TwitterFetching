from typing import Any, Dict, List
import uuid

from db import get_all_items, insert_item
from models.types import Location


def insert_user(
    location: Location, city: str, longitude_latitude: str
) -> Dict[str, Any]:
    """
    Insert a user item with the given location, city, and longitude_latitude.
    """
    user_id = uuid.uuid4().int % 10**38
    user_item = {
        "user_id": user_id,
        "location": location,
        "city": city,
        "longitude_latitude": longitude_latitude,
    }
    insert_item("User", user_item)

    return user_item


def get_users() -> List[Dict[str, Any]]:
    """
    Retrieves all user items from the database.
    """
    return get_all_items("User")
