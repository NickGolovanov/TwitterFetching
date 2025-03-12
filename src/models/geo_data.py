from typing import Any, Dict, List
import uuid

from db import get_all_items, insert_item


def insert_geo_data(
    search_query: str,
    start_time: str,
    end_time: str,
) -> None:
    """
    Insert a geo data item with the given search_query, start_time, and end_time.
    """
    geo_date_id = uuid.uuid4().int % 10**38
    geo_date_item = {
        "geo_date_id": geo_date_id,
        "search_query": search_query,
        "start_time": start_time,
        "end_time": end_time,
    }
    insert_item("GeoData", geo_date_item)


def get_geo_datas() -> List[Dict[str, Any]]:
    """
    Retrieves all geo data items from the database.
    """
    return get_all_items("User")
