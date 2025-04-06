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
ns = Namespace("user", description="User operations")

# Define models for documentation
user_model = ns.model(
    "User",
    {
        "user_id": fields.Integer(required=True, description="User identifier"),
        "location": fields.String(required=True, description="User location"),
        "city": fields.String(required=True, description="User city"),
        "longitude_latitude": fields.String(
            required=True, description="User coordinates"
        ),
    },
)

update_user_model = ns.model(
    "UpdateUser",
    {
        "location": fields.String(description="Updated user location"),
        "city": fields.String(description="Updated user city"),
        "longitude_latitude": fields.String(description="Updated user coordinates"),
    },
)


@ns.route("/")
class UserList(Resource):
    @ns.doc("get_users")
    @ns.response(200, "Success", [user_model])
    def get(self):
        """Get all users"""
        users = fetch_all_items(DYNAMODB_TABLES.get("User"))
        return jsonify(users)

    @ns.doc("create_user")
    @ns.expect(user_model)
    @ns.response(201, "User created successfully", user_model)
    @ns.response(400, "Bad request")
    def post(self):
        """Create a new user"""
        data = request.json
        if not data or "user_id" not in data:
            ns.abort(400, "Missing required 'user_id' field")

        table_name = DYNAMODB_TABLES.get("User")
        response = put_item(table_name, data)

        if response:
            return {"message": "User created successfully"}, 201
        else:
            ns.abort(500, "Failed to create User")


@ns.route("/<string:user_id>")
@ns.param("user_id", "The user identifier")
@ns.response(404, "User not found")
class UserItem(Resource):
    @ns.doc("get_user_by_id")
    @ns.response(200, "Success", user_model)
    def get(self, user_id):
        """Get user by ID"""
        user = fetch_item_by_key(DYNAMODB_TABLES.get("User"), "user_id", user_id)
        if user:
            return jsonify(user)
        else:
            ns.abort(404, message="User not found")

    @ns.doc("update_user")
    @ns.expect(update_user_model)
    @ns.response(200, "User updated successfully")
    @ns.response(400, "Bad request")
    def put(self, user_id):
        """Update existing user"""
        data = request.json
        if not data:
            ns.abort(400, "No update data provided")

        update_data = {k: v for k, v in data.items() if k not in ["user_id"]}

        table_name = DYNAMODB_TABLES.get("User")
        update_expression = "SET " + ", ".join(
            [f"#{key} = :{key}" for key in update_data.keys()]
        )
        expression_values = {f":{key}": value for key, value in update_data.items()}
        expression_names = {f"#{key}": key for key in update_data.keys()}

        response = update_item(
            table_name,
            {"user_id": int(user_id)},
            update_expression,
            expression_values,
            expression_names,
        )

        if response:
            return {"message": "User updated successfully"}, 200
        else:
            ns.abort(500, "Failed to update User")
