from flask import Blueprint, jsonify
from services.user_service import fetch_all_users

user_routes = Blueprint('user', __name__)

@user_routes.route('/get_users', methods=['GET'])
def get_users():
    users = fetch_all_users()
    return jsonify(users)
