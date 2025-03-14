from flask import Blueprint, jsonify
from services.dynamo_service import fetch_all_items,fetch_item_by_key
from config import DYNAMODB_TABLES

user_routes = Blueprint('user', __name__)

@user_routes.route('/', methods=['GET'])
def get_users():
    users = fetch_all_items(DYNAMODB_TABLES.get('User'))
    return jsonify(users)

@user_routes.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    user = fetch_item_by_key(user_id)
    if user: 
        return jsonify(user)
    else:
        return jsonify({"error: User not found"}), 404
