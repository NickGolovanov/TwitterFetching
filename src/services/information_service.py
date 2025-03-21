from config import AWS_REGION
import boto3 

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

def rehashe_link(hash):    
    table = dynamodb.Table('Users')
    response = table.scan()
    return response.get('Items', [])

def fetch_user_by_id(user_id):
    table = dynamodb.Table('Users')
    response = table.scan()
    return response.get('Items', [])