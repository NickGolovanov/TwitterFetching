import sys
import boto3
import time
from datetime import datetime
import threading

if "pytest" in sys.modules:
    from tests.test_config import AWS_REGION
else:
    from src.config import AWS_REGION

from src.database.data import (
    retrieve_x_posts,
    process_x_posts,
    validate_x_posts,
    analyze_x_posts,
    store_x_posts,
    notify_x_posts,
    insert_log_to_social_media,
    LogType,
)

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

collecting_data = threading.Event()


def data_pipeline() -> None:
    while not collecting_data.is_set():
        print("Starting Data Pipeline...")
        try:
            social_media_id, x_posts = retrieve_x_posts()
            if not x_posts:
                raise ValueError("No posts retrieved from X")

            processed_x_posts = process_x_posts(social_media_id, x_posts)
            if not processed_x_posts:
                raise ValueError("Failed to process X posts")

            validated_x_posts = validate_x_posts(social_media_id, processed_x_posts)
            if not validated_x_posts:
                raise ValueError("No posts passed validation")

            analyzed_x_posts = analyze_x_posts(social_media_id, validated_x_posts)
            if not analyzed_x_posts:
                raise ValueError("No posts passed analysis")

            stored_posts = store_x_posts(social_media_id, analyzed_x_posts)

            notify_x_posts(social_media_id, stored_posts)

            print(f"Successfully processed and stored {len(validated_x_posts)} posts")
        except Exception as e:
            print(f"Unexpected error in data pipeline: {e}")

            insert_log_to_social_media(
                social_media_id=social_media_id,  # type: ignore
                log={
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Unexpected error in data pipeline: {str(e)}",
                    "type": str(LogType.ERROR),
                },
            )
        print("Collecting Data...")

        if collecting_data.wait(timeout=3600):
            break
