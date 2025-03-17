from flask import Blueprint, jsonify
from services.dynamo_service import fetch_all_items, fetch_item_by_key
from config import DYNAMODB_TABLES

information_route = Blueprint('information', __name__)

@information_route.route('/', methods=["GET"])
def get_information():
    informations = fetch_all_items(DYNAMODB_TABLES.get("Information"))
    return jsonify(informations)

@information_route.route('/<information_id>', methods=["GET"])
def get_informations(information_id):
    information = fetch_item_by_key(DYNAMODB_TABLES.get("Information"), "information_id", information_id)
    if information:
        return jsonify(information)
    else:
        return jsonify({"error" : "No information found"}), 404