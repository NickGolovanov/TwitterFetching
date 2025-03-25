from typing import Any, Dict, List
import uuid

from ..db import get_all_items, insert_item


def insert_weather_alert(
    location: str,
    weather_type: str,
    date: str,
    map_link: str,
) -> Dict[str, Any]:
    """
    Insert an weather alert item with the given location, weather_type, date, and map_link.
    """
    weather_alert_id = uuid.uuid4().int % 10**38
    weather_alert_item = {
        "weather_alert_id": weather_alert_id,
        "weather_type": weather_type,
        "date": date,
        "location": location,
        "map_link": map_link,
    }

    insert_item("WeatherAlert", weather_alert_item)

    return weather_alert_item


def get_weather_alerts() -> List[Dict[str, Any]]:
    """
    Retrieves all information items from the database.
    """
    return get_all_items("WeatherAlert")
