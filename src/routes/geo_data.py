from flask import jsonify
from flask_restx import Namespace, Resource, fields
from services.dynamo_service import fetch_all_items, fetch_item_by_key
from config import DYNAMODB_TABLES

# Create namespace
ns = Namespace('geo_data', description='Geographic data operations')

# Define models for documentation
geo_data_model = ns.model('GeoData', {
    'geo_data_id': fields.String(required=True, description='Geographic data identifier'),
    'name': fields.String(description='Location name'),
    'coordinates': fields.String(description='Geographic coordinates'),
    # Add other fields that exist in your GeoData table
})

@ns.route('/')
class GeoDataList(Resource):
    @ns.doc('get_geo_data')
    @ns.response(200, 'Success', [geo_data_model])
    def get(self):
        """Get all geographic data locations"""
        geo_datas = fetch_all_items(DYNAMODB_TABLES.get("GeoData"))
        return jsonify(geo_datas)

@ns.route('/<string:geo_data_id>')
@ns.param('geo_data_id', 'The geographic data identifier')
@ns.response(404, 'Geographic data not found')
class GeoDataItem(Resource):
    @ns.doc('get_geo_data_by_id')
    @ns.response(200, 'Success', geo_data_model)
    def get(self, geo_data_id):
        """Get geographic data by ID"""
        geo_data = fetch_item_by_key(DYNAMODB_TABLES.get("GeoData"), "geo_data_id", geo_data_id)
        if geo_data:
            return jsonify(geo_data)
        else:
            ns.abort(404, message="No geo data found")