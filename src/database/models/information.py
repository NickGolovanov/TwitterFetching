from typing import Any, Dict, List
import uuid

from ..db import get_all_items, insert_item
from .types import Location


def insert_information(
    geo_data_id: int,
    location: Location,
    description: str,
    severity: str,
    weather_type: str,
    date: str,
    post_ids: List[int],
) -> Dict[str, Any]:
    """
    Insert an information item with the given geo_data_id, location, description, severity, weather_type, date, and post_ids.
    """
    information_id = uuid.uuid4().int
    information_item = {
        "information_id": information_id,
        "geo_data_id": geo_data_id,
        "location": location,
        "description": description,
        "severity": severity,
        "weather_type": weather_type,
        "date": date,
        "post_ids": post_ids,
    }
    insert_item("Information", information_item)

    return information_item


def get_informations() -> List[Dict[str, Any]]:
    """
    Retrieves all information items from the database.
    """
    return get_all_items("Information")
