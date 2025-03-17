from flask import Blueprint, jsonify
from services.dynamo_service import fetch_all_items, fetch_item_by_key
from config import DYNAMODB_TABLES

geo_data_route = Blueprint('geo_data', __name__)

@geo_data_route.route('/', methods=["GET"])
def get_geo_data():
    geo_datas = fetch_all_items(DYNAMODB_TABLES.get("GeoData"))
    return jsonify(geo_datas)

@geo_data_route.route('/<geo_data_id>', methods=["GET"])
def get_geo_datas(geo_data_id):
    geo_data = fetch_item_by_key(DYNAMODB_TABLES.get("GeoData"), "geo_data_id", geo_data_id)
    if geo_data:
        return jsonify(geo_data)
    else:
        return jsonify({"error" : "No geo data found"}), 404