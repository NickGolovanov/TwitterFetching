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
ns = Namespace("information", description="Information operations")

# Define models for documentation
information_model = ns.model(
    "Information",
    {
        "information_id": fields.String(
            required=True, description="Information identifier"
        ),
        "geo_data_id": fields.Integer(description="Geographic data identifier"),
        "location": fields.Raw(description="Location information"),
        "description": fields.String(description="Information description"),
        "severity": fields.String(description="Severity level"),
        "weather_type": fields.String(description="Type of weather event"),
        "date": fields.String(description="Date of the information"),
        "post_ids": fields.List(fields.Integer, description="Associated post IDs"),
    },
)

update_information_model = ns.model(
    "UpdateInformation",
    {
        "geo_data_id": fields.Integer(description="Updated geographic data identifier"),
        "location": fields.Raw(description="Updated location information"),
        "description": fields.String(description="Updated information description"),
        "severity": fields.String(description="Updated severity level"),
        "weather_type": fields.String(description="Updated type of weather event"),
        "date": fields.String(description="Updated date of the information"),
        "post_ids": fields.List(
            fields.Integer, description="Updated associated post IDs"
        ),
    },
)


@ns.route("/")
class InformationList(Resource):
    @ns.doc("get_information")
    @ns.response(200, "Success", [information_model])
    def get(self):
        """Get all information entries"""
        informations = fetch_all_items(DYNAMODB_TABLES.get("Information"))
        return jsonify(informations)

    @ns.doc("create_information")
    @ns.expect(information_model)
    @ns.response(201, "Information created successfully")
    @ns.response(400, "Bad request")
    def post(self):
        """Create new information"""
        data = request.json
        if not data or "information_id" not in data:
            ns.abort(400, "Missing required 'information_id' field")

        table_name = DYNAMODB_TABLES.get("Information")
        response = put_item(table_name, data)

        if response:
            return {"message": "Information created successfully"}, 201
        else:
            ns.abort(500, "Failed to create Information")


@ns.route("/<string:information_id>")
@ns.param("information_id", "The information identifier")
@ns.response(404, "Information not found")
class InformationItem(Resource):
    @ns.doc("get_information_by_id")
    @ns.response(200, "Success", information_model)
    def get(self, information_id):
        """Get information by ID"""
        information = fetch_item_by_key(
            DYNAMODB_TABLES.get("Information"), "information_id", information_id
        )
        if information:
            return jsonify(information)
        else:
            ns.abort(404, message="No information found")

    @ns.doc("update_information")
    @ns.expect(update_information_model)
    @ns.response(200, "Information updated successfully")
    @ns.response(400, "Bad request")
    def put(self, information_id):
        """Update existing information"""
        data = request.json
        if not data:
            ns.abort(400, "No update data provided")

        update_data = {
            k: v for k, v in data.items() if k not in ["information_id", "geo_data_id"]
        }

        table_name = DYNAMODB_TABLES.get("Information")
        update_expression = "SET " + ", ".join(
            [f"#{key} = :{key}" for key in update_data.keys()]
        )
        expression_values = {f":{key}": value for key, value in update_data.items()}
        expression_names = {f"#{key}": key for key in update_data.keys()}

        response = update_item(
            table_name,
            {
                "information_id": int(information_id),
                "geo_data_id": int(data["geo_data_id"]),
            },
            update_expression,
            expression_values,
            expression_names,
        )
        if response:
            return {"message": "Information updated successfully"}, 200
        else:
            ns.abort(500, "Failed to update Information")
