from typing import Any, Dict, List
import uuid
from db import get_all_items, insert_item
from models.types import Location


def insert_post(
    social_media_id: int,
    location: Location,
    description: str,
    severity: str,
    weather_type: str,
    date: str,
    id: int,
) -> None:
    """
    Insert a post item with the given social_media_id, location, description, severity, weather_type, date, and id.
    """
    post_id = uuid.uuid4().int % 10**38
    post_item = {
        "post_id": post_id,
        "social_media_id": social_media_id,
        "location": location,
        "description": description,
        "severity": severity,
        "weather_type": weather_type,
        "date": date,
        "id": id,
    }
    insert_item("Post", post_item)


def get_posts() -> List[Dict[str, Any]]:
    """
    Retrieves all post items from the database.
    """
    return get_all_items("Post")
