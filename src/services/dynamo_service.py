import boto3
from config import AWS_REGION

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

def fetch_all_items(table_name):
    table_name = dynamodb.Table(table_name)
    try:
        response = table.scan()
        return response.get('Items', [])
    except Exception as e:
        print(f"Error occuser form {table_name}: {e}")
        return []

def fetch_item_by_key(table_name, key):
    table_name = dynamodb.Table(table_name)
    try:
        response = table.get_item(Key=key)
        return response.get('Item', None)
    except Exception as e:
        print(f"Error occuser form {table_name}: {e}")
        return []
