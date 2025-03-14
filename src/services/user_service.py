from config import AWS_REGION
import boto3 

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

def fetch_users_by_id(user_id:list):
    table = dynamodb.Table('Users')
    response = table.scan()
    return response.get('Items', [])