from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from src.services.dynamo_service import (
    fetch_all_items,
    fetch_item_by_key,
    put_item,
    update_item,
)
from src.config import DYNAMODB_TABLES

# Create namespace
ns = Namespace("geo_data", description="Geographic data operations")

# Define models for documentation
geo_data_model = ns.model(
    "GeoData",
    {
        "geo_data_id": fields.String(
            required=True, description="Geographic data identifier"
        ),
        "search_query": fields.String(description="Query used to search for data"),
        "start_time": fields.String(description="Start time of search"),
        "end_time": fields.String(description="End time of search"),
    },
)

update_geo_data_model = ns.model(
    "UpdateGeoData",
    {
        "search_query": fields.String(description="Updated search query"),
        "start_time": fields.String(description="Updated start time"),
        "end_time": fields.String(description="Updated end time"),
    },
)


@ns.route("/")
class GeoDataList(Resource):
    @ns.doc("get_geo_data")
    @ns.response(200, "Success", [geo_data_model])
    def get(self):
        """Get all geographic data locations"""
        geo_datas = fetch_all_items(DYNAMODB_TABLES.get("GeoData"))
        return jsonify(geo_datas)

    @ns.doc("create_geo_data")
    @ns.expect(geo_data_model)
    @ns.response(201, "GeoData created successfully")
    @ns.response(400, "Bad request")
    def post(self):
        """Create new geographic data"""
        data = request.json
        if not data or "geo_data_id" not in data:
            ns.abort(400, "Missing required 'geo_data_id' field")

        table_name = DYNAMODB_TABLES.get("GeoData")
        response = put_item(table_name, data)

        if response:
            return {"message": "GeoData created successfully"}, 201
        else:
            ns.abort(500, "Failed to create GeoData")


@ns.route("/<string:geo_data_id>")
@ns.param("geo_data_id", "The geographic data identifier")
@ns.response(404, "Geographic data not found")
class GeoDataItem(Resource):
    @ns.doc("get_geo_data_by_id")
    @ns.response(200, "Success", geo_data_model)
    def get(self, geo_data_id):
        """Get geographic data by ID"""
        geo_data = fetch_item_by_key(
            DYNAMODB_TABLES.get("GeoData"), "geo_data_id", geo_data_id
        )
        if geo_data:
            return jsonify(geo_data)
        else:
            ns.abort(404, message="No geo data found")

    @ns.doc("update_geo_data")
    @ns.expect(update_geo_data_model)
    @ns.response(200, "GeoData updated successfully")
    @ns.response(400, "Bad request")
    def put(self, geo_data_id):
        """Update existing geographic data"""
        data = request.json
        if not data:
            ns.abort(400, "No update data provided")

        update_data = {k: v for k, v in data.items() if k not in ["geo_data_id"]}

        table_name = DYNAMODB_TABLES.get("GeoData")
        update_expression = "SET " + ", ".join(
            [f"#{key} = :{key}" for key in update_data.keys()]
        )
        expression_values = {f":{key}": value for key, value in update_data.items()}
        expression_names = {f"#{key}": key for key in update_data.keys()}

        response = update_item(
            table_name,
            {"geo_data_id": int(geo_data_id)},
            update_expression,
            expression_values,
            expression_names,
        )

        if response:
            return {"message": "GeoData updated successfully"}, 200
        else:
            ns.abort(500, "Failed to update GeoData")
