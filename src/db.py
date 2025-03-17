import os
import uuid
from typing import TypedDict, Optional, List, Dict, Any
from enum import Enum
from dotenv import load_dotenv


import boto3

from botocore.exceptions import ClientError

from types_boto3_dynamodb.type_defs import (
    KeySchemaElementTypeDef,
    AttributeDefinitionTypeDef,
    GlobalSecondaryIndexUnionTypeDef,
    ProvisionedThroughputTypeDef,
)

from types_boto3_dynamodb.client import DynamoDBClient
from types_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")


def get_dynamodb_client() -> DynamoDBClient:
    return boto3.client(
        "dynamodb",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def get_dynamodb_resource() -> DynamoDBServiceResource:
    return boto3.resource(
        "dynamodb",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


dynamodb_client: DynamoDBClient = get_dynamodb_client()
dynamodb_resource: DynamoDBServiceResource = get_dynamodb_resource()


def is_table_exists(client: DynamoDBClient, table_name: str) -> bool:
    """Return True if table_name exists in DynamoDB, else False."""
    try:
        client.describe_table(TableName=table_name)
        return True
    except client.exceptions.ResourceNotFoundException as e:
        print(f"Table {table_name} not found in DynamoDB: {e}")
        return False
    except ClientError as e:
        print(f"Error checking if table '{table_name}' exists: {e}")
        raise


def create_table_if_not_exists(
    client: DynamoDBClient,
    table_name: str,
    key_schema: List[KeySchemaElementTypeDef],
    attribute_definitions: List[AttributeDefinitionTypeDef],
    global_secondary_indexes: Optional[List[GlobalSecondaryIndexUnionTypeDef]] = None,
    provisioned_throughput: ProvisionedThroughputTypeDef = {
        "ReadCapacityUnits": 5,
        "WriteCapacityUnits": 5,
    },
) -> None:
    """
    If the given table does not exist, creates it with the provided key schema,
    attribute definitions, and provisioned throughput.
    """
    if is_table_exists(client, table_name):
        print(f"Table '{table_name}' already exists.")
    else:
        print(f"Creating table '{table_name}'...")

        try:
            client.create_table(
                TableName=table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definitions,
                GlobalSecondaryIndexes=global_secondary_indexes,
                ProvisionedThroughput=provisioned_throughput,
            )

            # Wait until the table exists (active)
            waiter = client.get_waiter("table_exists")
            waiter.wait(TableName=table_name)
            print(f"Table '{table_name}' created.")
        except ClientError as e:
            print(f"Error creating table '{table_name}': {e}")
            raise


def create_main_tables_if_not_exist(client: DynamoDBClient) -> None:
    """
    Creates the tables SocialMedia, Post, GeoData, Information, User
    if they do not already exist.
    """

    # SocialMedia
    create_table_if_not_exists(
        client,
        table_name="SocialMedia",
        key_schema=[{"AttributeName": "social_media_id", "KeyType": "HASH"}],
        attribute_definitions=[
            {"AttributeName": "social_media_id", "AttributeType": "N"}
        ],
    )

    # Post
    create_table_if_not_exists(
        client,
        table_name="Post",
        key_schema=[
            {"AttributeName": "post_id", "KeyType": "HASH"},
            {"AttributeName": "social_media_id", "KeyType": "RANGE"},
        ],
        attribute_definitions=[
            {"AttributeName": "post_id", "AttributeType": "N"},
            {"AttributeName": "social_media_id", "AttributeType": "N"},
            {"AttributeName": "id", "AttributeType": "N"},
            {"AttributeName": "description", "AttributeType": "S"},
        ],
        global_secondary_indexes=[
            {
                "IndexName": "id-description-index",
                "KeySchema": [
                    {"AttributeName": "id", "KeyType": "HASH"},
                    {"AttributeName": "description", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            }
        ],
    )

    # GeoData
    create_table_if_not_exists(
        client,
        table_name="GeoData",
        key_schema=[{"AttributeName": "geo_data_id", "KeyType": "HASH"}],
        attribute_definitions=[{"AttributeName": "geo_data_id", "AttributeType": "N"}],
    )

    # Information
    create_table_if_not_exists(
        client,
        table_name="Information",
        key_schema=[
            {"AttributeName": "information_id", "KeyType": "HASH"},
            {"AttributeName": "geo_data_id", "KeyType": "RANGE"},
        ],
        attribute_definitions=[
            {"AttributeName": "information_id", "AttributeType": "N"},
            {"AttributeName": "geo_data_id", "AttributeType": "N"},
        ],
    )

    # User
    create_table_if_not_exists(
        client,
        table_name="User",
        key_schema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
        attribute_definitions=[{"AttributeName": "user_id", "AttributeType": "N"}],
    )


def insert_item(table_name: str, item: Dict[str, Any]) -> None:
    """
    Insert (Put) an item into the specified table.
    Overwrites if an item with the same key already exists.
    """
    try:
        table: Table = dynamodb_resource.Table(table_name)
        table.put_item(Item=item)
        print(f"Inserted item into '{table_name}': {item}")
    except ClientError as e:
        print(f"Error inserting item into table '{table_name}': {e}")
        raise


def get_item(table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get a single item by its primary key.
    Returns the item dict if found, otherwise None.
    """
    try:
        table: Table = dynamodb_resource.Table(table_name)
        response = table.get_item(Key=key)
        return response.get("Item")
    except ClientError as e:
        print(f"Error getting item from table '{table_name}': {e}")
        raise


def update_item(
    table_name: str,
    key: Dict[str, Any],
    update_expression: str,
    expression_attribute_values: Dict[str, Any],
    expression_attribute_names: Optional[Dict[str, str]] = None,
) -> None:
    """
    Update an item using an UpdateExpression.
    Example:
        update_expression = "SET #attr = :val"
        expression_attribute_values = {":val": 123}
        expression_attribute_names = {"#attr": "some_attribute"}
    """
    try:
        table: Table = dynamodb_resource.Table(table_name)
        kwargs: Dict[str, Any] = {
            "Key": key,
            "UpdateExpression": update_expression,
            "ExpressionAttributeValues": expression_attribute_values,
        }
        if expression_attribute_names is not None:
            kwargs["ExpressionAttributeNames"] = expression_attribute_names

        table.update_item(**kwargs)
        print(f"Updated item in '{table_name}' with key={key}")
    except ClientError as e:
        print(f"Error updating item in table '{table_name}': {e}")
        raise


def delete_item(table_name: str, key: Dict[str, Any]) -> None:
    """
    Delete an item by its primary key.
    """
    try:
        table: Table = dynamodb_resource.Table(table_name)
        table.delete_item(Key=key)
        print(f"Deleted item from '{table_name}' with key={key}")
    except ClientError as e:
        print(f"Error deleting item from table '{table_name}': {e}")
        raise


def get_all_items(table_name: str) -> List[Dict[str, Any]]:
    """
    Get all items from the specified table.
    """
    try:
        table: Table = dynamodb_resource.Table(table_name)
        response = table.scan()
        items = response.get("Items", [])
        print(f"Retrieved {len(items)} items from '{table_name}'")
        return items
    except ClientError as e:
        print(f"Error querying items from table '{table_name}': {e}")
        raise


def query_items(
    table_name: str,
    key_condition_expression: str,
    expression_attribute_values: Dict[str, Any],
    expression_attribute_names: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Query items with a KeyConditionExpression.
    Example:
        key_condition_expression = "post_id = :pid"
        expression_attribute_values = {":pid": 100}
    """
    try:
        table: Table = dynamodb_resource.Table(table_name)
        kwargs: Dict[str, Any] = {
            "KeyConditionExpression": key_condition_expression,
            "ExpressionAttributeValues": expression_attribute_values,
        }
        if expression_attribute_names:
            kwargs["ExpressionAttributeNames"] = expression_attribute_names

        response = table.query(**kwargs)
        items = response.get("Items", [])
        print(f"Queried {len(items)} items from '{table_name}'")
        return items
    except ClientError as e:
        print(f"Error querying items from table '{table_name}': {e}")
        raise
