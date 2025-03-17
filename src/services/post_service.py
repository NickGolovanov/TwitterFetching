import requests
import boto3
from config import AWS_REGION

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

def fetch_data_by_post_ids(post_ids):
    table = dynamodb.Table('Post')
    keys = [{'post_id': post_id} for post_id in post_ids]

    response = dynamodb.batch_get_item(
        RequestItems={
            'Post': {
                'Keys': keys
            }
        }
    )

    return response.get('Responses', {}).get('Post', [])

def rehash_the_link(link):
    try:
        response = requests.get(link)
        response.raise_for_status()

        data = response.json()

        post_ids = data.get('post_ids', [])

        if not post_ids:
            return {"error": "No post_ids found in the data."}

        return post_ids

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}

def fetch_data_from_link(link):
    post_ids = rehash_the_link(link)

    if isinstance(post_ids, dict) and 'error' in post_ids:
        return post_ids

    posts_data = fetch_data_by_post_ids(post_ids)

    return {"posts": posts_data}
