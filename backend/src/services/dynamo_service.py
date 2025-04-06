import boto3
from boto3.dynamodb.conditions import Key
import sys

if "pytest" in sys.modules:
    from tests.test_config import AWS_REGION
else:
    from src.config import AWS_REGION

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)


def fetch_all_items(table_name):
    table = dynamodb.Table(table_name)
    try:
        items = []

        response = table.scan()
        items.extend(response.get("Items", []))

        while response.get("LastEvaluatedKey"):
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))

        return items

    except Exception as e:
        print(f"Error occuser form {table_name}: {e}")
        return None


def fetch_item_by_key(table_name, key_name, key):
    table = dynamodb.Table(table_name)
    try:
        response = table.query(KeyConditionExpression=Key(key_name).eq(int(key)))
        print(response)
        return response.get("Items", None)
    except Exception as e:
        print(f"Error occurred from {table_name}: {e}")
        return []


def put_item(table_name, item):
    """Put (create or replace) an item in the DynamoDB table."""
    table = dynamodb.Table(table_name)
    try:
        response = table.put_item(Item=item)
        return response
    except Exception as e:
        print(f"Error occurred while putting item in {table_name}: {e}")
        return None


def update_item(
    table_name, key, update_expression, expression_values, expression_names
):
    """
    Update an existing item in the DynamoDB table.

    Parameters:
        table_name (str): The table name.
        key (dict): The key of the item to update.
        update_expression (str): The update expression.
        expression_values (dict): A dictionary of expression attribute values.
        expression_names (dict): A dictionary of expression attribute names.

    Example:
        update_item("Users", {"user_id": 123}, "SET age = :age", {":age": 30}, {":age": "age"})
    """
    table = dynamodb.Table(table_name)
    try:
        response = table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names,
            ReturnValues="UPDATED_NEW",
        )
        return response
    except Exception as e:
        print(f"Error occurred while updating item in {table_name}: {e}")
        return None
