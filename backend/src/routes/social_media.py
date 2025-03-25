from flask import jsonify
from flask_restx import Namespace, Resource, fields
from services.dynamo_service import fetch_all_items, fetch_item_by_key
from config import DYNAMODB_TABLES

# Create namespace
ns = Namespace("social_media", description="Social media operations")

# Define models for documentation
social_media_model = ns.model(
    "SocialMedia",
    {
        "social_media_id": fields.Integer(
            required=True, description="Social media identifier"
        ),
        "search_query": fields.String(description="Search query used"),
        "start_time": fields.String(description="Start time of the search"),
        "end_time": fields.String(description="End time of the search"),
        "logs": fields.List(fields.Raw, description="List of logs"),
    },
)


@ns.route("/")
class SocialMediaList(Resource):
    @ns.doc("get_social_media")
    @ns.response(200, "Success", [social_media_model])
    def get(self):
        """Get all social media entries"""
        social_medias = fetch_all_items(DYNAMODB_TABLES.get("SocialMedia"))
        return jsonify(social_medias)


@ns.route("/<string:social_media_id>")
@ns.param("social_media_id", "The social media identifier")
@ns.response(404, "Social media not found")
class SocialMediaItem(Resource):
    @ns.doc("get_social_media_by_id")
    @ns.response(200, "Success", social_media_model)
    def get(self, social_media_id):
        """Get social media by ID"""
        social_media = fetch_item_by_key(
            DYNAMODB_TABLES.get("SocialMedia"), "social_media_id", social_media_id
        )
        if social_media:
            return jsonify(social_media)
        else:
            ns.abort(404, message="Social media not found")
