from boto3.dynamodb.conditions import And, Attr, Key, Or
import boto3
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from config import AWS_REGION


dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

load_dotenv()

HASHING_SECRET = os.getenv("HASHING_SECRET", "")

cipher_suite = Fernet(HASHING_SECRET)


def encrypt_data(plain_text: str) -> bytes:
    encrypted_text = cipher_suite.encrypt(plain_text.encode())
    return encrypted_text


def decrypt_data(encrypted_text: bytes) -> str:
    decrypted_text = cipher_suite.decrypt(encrypted_text).decode()
    return decrypted_text


def fetch_data_by_post_ids(post_ids):
    table = dynamodb.Table("Post")
    if not post_ids:
        return []

    filter_expression = Attr("post_id").is_in(map(int, post_ids))

    response = table.scan(FilterExpression=filter_expression)

    items = response["Items"]

    while "LastEvaluatedKey" in response:
        response = table.scan(
            FilterExpression=filter_expression,
            ExclusiveStartKey=response["LastEvaluatedKey"],
        )
        items.extend(response["Items"])

    return items


def rehash_the_link(link):
    try:
        post_ids = decrypt_data(link.encode()).split(",")

        if not post_ids:
            return {"error": "No post_ids found in the data."}

        return list(set(post_ids))

    except Exception as e:
        return {"error": str(e)}


def fetch_data_from_link(link):
    post_ids = rehash_the_link(link)

    if isinstance(post_ids, dict) and "error" in post_ids:
        return post_ids

    posts_data = fetch_data_by_post_ids(post_ids)

    return {"posts": posts_data}
