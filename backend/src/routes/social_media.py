from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from src.services.dynamo_service import (
    fetch_all_items,
    fetch_item_by_key,
    put_item,
    update_item,
)
from src.config import DYNAMODB_TABLES

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

update_social_media_model = ns.model(
    "UpdateSocialMedia",
    {
        "search_query": fields.String(description="Updated search query"),
        "start_time": fields.String(description="Updated start time"),
        "end_time": fields.String(description="Updated end time"),
        "logs": fields.List(fields.Raw, description="Updated list of logs"),
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

    @ns.doc("create_social_media")
    @ns.expect(social_media_model)
    @ns.response(201, "Social Media created successfully", social_media_model)
    @ns.response(400, "Bad request")
    def post(self):
        """Create new social media entry"""
        data = request.json
        if not data or "social_media_id" not in data:
            ns.abort(400, "Missing required 'social_media_id' field")

        table_name = DYNAMODB_TABLES.get("SocialMedia")
        response = put_item(table_name, data)

        if response:
            return {"message": "Social Media created successfully"}, 201
        else:
            ns.abort(500, "Failed to create Social Media")


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

    @ns.doc("update_social_media")
    @ns.expect(update_social_media_model)
    @ns.response(200, "Social Media updated successfully")
    @ns.response(400, "Bad request")
    def put(self, social_media_id):
        """Update existing social media entry"""
        data = request.json
        if not data:
            ns.abort(400, "No update data provided")

        update_data = {k: v for k, v in data.items() if k not in ["social_media_id"]}

        table_name = DYNAMODB_TABLES.get("SocialMedia")
        update_expression = "SET " + ", ".join(
            [f"#{key} = :{key}" for key in update_data.keys()]
        )
        expression_values = {f":{key}": value for key, value in update_data.items()}
        expression_names = {f"#{key}": key for key in update_data.keys()}

        response = update_item(
            table_name,
            {"social_media_id": int(social_media_id)},
            update_expression,
            expression_values,
            expression_names,
        )

        if response:
            return {"message": "Social Media updated successfully"}, 200
        else:
            ns.abort(500, "Failed to update Social Media")
