from flask import jsonify
from flask_restx import Namespace, Resource, fields
from services.dynamo_service import fetch_all_items, fetch_item_by_key
from config import DYNAMODB_TABLES

# Create namespace
ns = Namespace('information', description='Information operations')

# Define models for documentation
information_model = ns.model('Information', {
    'information_id': fields.String(required=True, description='Information identifier'),
    'title': fields.String(description='Information title'),
    'content': fields.String(description='Information content'),
    # Add other fields that exist in your Information table
})

@ns.route('/')
class InformationList(Resource):
    @ns.doc('get_information')
    @ns.response(200, 'Success', [information_model])
    def get(self):
        """Get all information entries"""
        informations = fetch_all_items(DYNAMODB_TABLES.get("Information"))
        return jsonify(informations)

@ns.route('/<string:information_id>')
@ns.param('information_id', 'The information identifier')
@ns.response(404, 'Information not found')
class InformationItem(Resource):
    @ns.doc('get_information_by_id')
    @ns.response(200, 'Success', information_model)
    def get(self, information_id):
        """Get information by ID"""
        information = fetch_item_by_key(DYNAMODB_TABLES.get("Information"), "information_id", information_id)
        if information:
            return jsonify(information)
        else:
            ns.abort(404, message="No information found")