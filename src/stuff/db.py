import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os

load_dotenv()

TABLE_NAME = "tweets"

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")

ITEMS = [
    {
        "id": 1,
        "sort": "ACS",
        "tweet_link": "https://twitter.com/elonmusk/status/1234567890",
    },
    {
        "id": 2,
        "sort": "ACS",
        "tweet_link": "https://twitter.com/elonmusk/status/1234567890",
    },
    {
        "id": 3,
        "sort": "ACS",
        "tweet_link": "https://twitter.com/elonmusk/status/1234567890",
    },
]


def connect_to_dynamodb():
    try:
        dynamodb = boto3.resource(
            "dynamodb",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        return dynamodb.Table(TABLE_NAME)
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


def main():
    table = connect_to_dynamodb()
    if table:
        insert_data(table, ITEMS)


if __name__ == "__main__":
    main()
