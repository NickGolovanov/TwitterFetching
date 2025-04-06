from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from src.services.dynamo_service import (
    fetch_all_items,
    fetch_item_by_key,
    put_item,
    update_item,
)
from src.services.post_service import fetch_data_from_link
from src.config import DYNAMODB_TABLES

# Create namespace
ns = Namespace("post", description="Post operations")

# Define models for documentation
post_model = ns.model(
    "Post",
    {
        "post_id": fields.String(required=True, description="Post identifier"),
        "social_media_id": fields.Integer(description="Social media identifier"),
        "location": fields.Raw(description="Location information"),
        "description": fields.String(description="Post description"),
        "severity": fields.String(description="Severity level"),
        "weather_type": fields.String(description="Type of weather event"),
        "date": fields.String(description="Date of the post"),
        "id": fields.Integer(description="Original post ID"),
        "tweet_link": fields.String(description="Tweet link"),
    },
)

update_post_model = ns.model(
    "UpdatePost",
    {
        "social_media_id": fields.Integer(
            description="Updated social media identifier"
        ),
        "location": fields.Raw(description="Updated location information"),
        "description": fields.String(description="Updated post description"),
        "severity": fields.String(description="Updated severity level"),
        "weather_type": fields.String(description="Updated weather event type"),
        "date": fields.String(description="Updated post date"),
        "id": fields.Integer(description="Updated original post ID"),
        "tweet_link": fields.String(description="Updated tweet link"),
    },
)


@ns.route("/")
class PostList(Resource):
    @ns.doc("get_posts")
    @ns.response(200, "Success", [post_model])
    def get(self):
        """Get all posts"""
        posts = fetch_all_items(DYNAMODB_TABLES.get("Post"))

        # Sort posts by date in descending order (newest first)
        if posts:
            posts = sorted(posts, key=lambda post: post.get("date", ""), reverse=True)

        return jsonify(posts)

    @ns.doc("create_post")
    @ns.expect(post_model)
    @ns.response(201, "Post created successfully", post_model)
    @ns.response(400, "Bad request")
    def post(self):
        """Create new post"""
        data = request.json
        if not data or "post_id" not in data:
            ns.abort(400, "Missing required 'post_id' field")

        table_name = DYNAMODB_TABLES.get("Post")
        response = put_item(table_name, data)

        if response:
            return {"message": "Post created successfully"}, 201
        else:
            ns.abort(500, "Failed to create Post")


@ns.route("/<string:post_id>")
@ns.param("post_id", "The post identifier")
@ns.response(404, "Post not found")
class PostItem(Resource):
    @ns.doc("get_post_by_id")
    @ns.response(200, "Success", post_model)
    def get(self, post_id):
        """Get post by ID"""
        post = fetch_item_by_key(DYNAMODB_TABLES.get("Post"), "post_id", post_id)
        if post:
            return jsonify(post)
        else:
            ns.abort(404, message="No post found")

    @ns.doc("update_post")
    @ns.expect(update_post_model)
    @ns.response(200, "Post updated successfully")
    @ns.response(400, "Bad request")
    def put(self, post_id):
        """Update existing post"""
        data = request.json
        if not data:
            ns.abort(400, "No update data provided")

        # Remove key fields from update data
        update_data = {
            k: v for k, v in data.items() if k not in ["post_id", "social_media_id"]
        }

        table_name = DYNAMODB_TABLES.get("Post")
        update_expression = "SET " + ", ".join(
            [f"#{key} = :{key}" for key in update_data.keys()]
        )
        expression_values = {f":{key}": value for key, value in update_data.items()}
        expression_names = {f"#{key}": key for key in update_data.keys()}

        response = update_item(
            table_name,
            {"post_id": int(post_id), "social_media_id": int(data["social_media_id"])},
            update_expression,
            expression_values,
            expression_names,
        )

        if response:
            return {"message": "Post updated successfully"}, 200
        else:
            ns.abort(500, "Failed to update Post")


@ns.route("/rehash/<path:link>")
@ns.param("link", "The link to extract data from")
class RehashPost(Resource):
    @ns.doc("rehash_post_data")
    @ns.response(200, "Success", [post_model])
    @ns.response(400, "Bad request")
    def get(self, link):
        """Extract and rehash data from a provided link"""
        result = fetch_data_from_link(link)

        if "error" in result:
            ns.abort(400, message="No post IDs found in the data.")
        else:
            return jsonify(result)
