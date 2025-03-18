from flask import jsonify
from flask_restx import Namespace, Resource, fields
from services.dynamo_service import fetch_all_items, fetch_item_by_key
from config import DYNAMODB_TABLES

# Create namespace
ns = Namespace('user', description='User operations')

# Define models for documentation
user_model = ns.model('User', {
    'user_id': fields.String(required=True, description='User identifier'),
    'name': fields.String(description='User name'),
    'email': fields.String(description='User email'),
    # Add other fields that exist in your User table
})

@ns.route('/')
class UserList(Resource):
    @ns.doc('get_users')
    @ns.response(200, 'Success', [user_model])
    def get(self):
        """Get all users"""
        users = fetch_all_items(DYNAMODB_TABLES.get('User'))
        return jsonify(users)

@ns.route('/<string:user_id>')
@ns.param('user_id', 'The user identifier')
@ns.response(404, 'User not found')
class UserItem(Resource):
    @ns.doc('get_user_by_id')
    @ns.response(200, 'Success', user_model)
    def get(self, user_id):
        """Get user by ID"""
        user = fetch_item_by_key(DYNAMODB_TABLES.get('User'), "user_id", user_id)
        if user:
            return jsonify(user)
        else:
            ns.abort(404, message="User not found")