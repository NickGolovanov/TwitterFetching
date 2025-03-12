from typing import Any, Dict, List
import uuid

from db import get_all_items, insert_item, update_item
from models.types import Log


def insert_social_media(
    search_query: str, start_time: str, end_time: str, logs: List[Log]
) -> None:
    """
    Insert a social media item with the given search_query, start_time, end_time, and logs.
    """
    social_media_id = uuid.uuid4().int % 10**38
    social_media_item = {
        "social_media_id": social_media_id,
        "search_query": search_query,
        "start_time": start_time,
        "end_time": end_time,
        "logs": logs,
    }
    insert_item("SocialMedia", social_media_item)


def insert_log_to_social_media(social_media_id: int, log: Log) -> None:
    """
    Insert a log into an existing social media item's logs array.
    """
    update_item(
        table_name="SocialMedia",
        key={"social_media_id": social_media_id},
        update_expression="SET logs = list_append(if_not_exists(logs, :empty_list), :log)",
        expression_attribute_values={":log": [log], ":empty_list": []},
    )


def get_social_medias() -> List[Dict[str, Any]]:
    """
    Retrieves all social media items from the database.
    """
    return get_all_items("SocialMedia")


def get_logs() -> List[Dict[str, Any]]:
    """
    Retrieves all logs from all social media items in the database.
    """
    social_medias = get_social_medias()

    logs = []

    for social_media in social_medias:
        logs.extend(social_media["logs"])

    return logs
