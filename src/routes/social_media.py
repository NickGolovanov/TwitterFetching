from services.dynamo_service import fetch_all_items, fetch_item_by_key
from config import DYNAMODB_TABLES
from flask import Blueprint, jsonify

social_media_routes = Blueprint('social_media', __name__)

@social_media_routes.route('/', methods=["GET"])
def get_social_media():
    social_medias = fetch_all_items(DYNAMODB_TABLES.get('SocialMedia'))
    return jsonify(social_medias)

@social_media_routes.route('/<social_media_id>', methods=["GET"])
def get_social_media(social_media_id):
    social_media = fetch_item_by_key(social_media_id)
    if social_media:
        return jsonify(social_media)
    else:
        return jsonify({"error: SocialMedia not found"}), 404