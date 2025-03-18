from datetime import datetime
from typing import Any
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")

ITEMS = [
    {
        "post_id": 1,
        "social_media_id": 1,
        "location_id": 1,
        "tweet_link": "https://twitter.com/elonmusk/status/1234567890",
    },
    {
        "post_id": 2,
        "social_media_id": 1,
        "location_id": 1,
        "tweet_link": "https://twitter.com/elonmusk/status/1234567890",
    },
    {
        "post_id": 3,
        "social_media_id": 1,
        "location_id": 1,
        "tweet_link": "https://twitter.com/elonmusk/status/1234567890",
    },
]


def make_post_item(
    post_id: int,
    # social_media_id: int,
    # location_id: int,
    descritpion: str,
    # severity: str,
    # weather_type: str,
    date: datetime,
    id: str,
):
    return {
        "post_id": post_id,
        "social_media_id": 0,
        "location_id": 0,
        "descritpion": descritpion,
        "severity": "normal",
        "weather_type": "unknown",
        "date": date.strftime("%Y-%m-%d %H:%M:%S"),
        "id": id,
    }


def connect_to_dynamodb_table(table_name):
    try:
        dynamodb: Any = boto3.resource(
            "dynamodb",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        return dynamodb.Table(table_name)
    except (NoCredentialsError, PartialCredentialsError):
        print("AWS credentials not found. Configure them using `aws configure`.")
        return None


def insert_data(table, items):
    for item in items:
        try:
            table.put_item(Item=item)
            print(f"Inserted: {item}")
        except Exception as e:
            print(f"Error inserting {item}: {e}")
