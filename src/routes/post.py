from flask import Blueprint, jsonify
from services.dynamo_service import fetch_all_items, fetch_item_by_key
from services.post_service import fetch_data_from_link
from config import DYNAMODB_TABLES

post_route = Blueprint('post', __name__)

@post_route.route('/', methods=["GET"])
def get_posts():
    routes = fetch_all_items(DYNAMODB_TABLES.get("Post"))
    return jsonify(routes)

@post_route.route('/<post_id>', methods=["GET"])
def get_post(post_id):
    post = fetch_item_by_key(DYNAMODB_TABLES.get("Post"), "post_id", post_id)
    print(post)
    if post:
        return jsonify(post)
    else:
        return jsonify({"error" : "No post found"}), 404
    
@post_route.route('/rehash/<link>', methods=['GET'])
def rehash_post_data(link):
    result = fetch_data_from_link(link)

    if 'error' in result:
        return jsonify({"error": result['error']}), 400
    return jsonify({"error": "No post IDs found in the data."}), 404
