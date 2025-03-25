import boto3
from boto3.dynamodb.conditions import Key
from config import AWS_REGION
import boto3

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
