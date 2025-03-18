from config import AWS_REGION
import boto3
import time
from datetime import datetime

from database.data import retrieve_x_posts, process_x_posts, validate_x_posts, store_x_posts, insert_log_to_social_media, LogType

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

collecting_data = False

def data_pipeline() -> None:
    
    global collecting_data
    while collecting_data:
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

            store_x_posts(social_media_id, validated_x_posts)
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
        time.sleep(3600)