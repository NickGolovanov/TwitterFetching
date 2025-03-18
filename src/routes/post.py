from flask import jsonify
from flask_restx import Namespace, Resource, fields
from services.dynamo_service import fetch_all_items, fetch_item_by_key
from services.post_service import fetch_data_from_link
from config import DYNAMODB_TABLES

# Create namespace
ns = Namespace('post', description='Post operations')

# Define models for documentation
post_model = ns.model('Post', {
    'post_id': fields.String(required=True, description='Post identifier'),
    'title': fields.String(description='Post title'),
    'content': fields.String(description='Post content'),
    # Add other fields that exist in your Post table
})

rehash_model = ns.model('RehashResult', {
    'success': fields.Boolean(description='Operation status'),
    'data': fields.Raw(description='Extracted data'),
    # Add other fields that may be returned by fetch_data_from_link
})

@ns.route('/')
class PostList(Resource):
    @ns.doc('get_posts')
    @ns.response(200, 'Success', [post_model])
    def get(self):
        """Get all posts"""
        posts = fetch_all_items(DYNAMODB_TABLES.get("Post"))
        return jsonify(posts)

@ns.route('/<string:post_id>')
@ns.param('post_id', 'The post identifier')
@ns.response(404, 'Post not found')
class PostItem(Resource):
    @ns.doc('get_post_by_id')
    @ns.response(200, 'Success', post_model)
    def get(self, post_id):
        """Get post by ID"""
        post = fetch_item_by_key(DYNAMODB_TABLES.get("Post"), "post_id", post_id)
        if post:
            return jsonify(post)
        else:
            ns.abort(404, message="No post found")

@ns.route('/rehash/<string:link>')
@ns.param('link', 'The link to extract data from')
class RehashPost(Resource):
    @ns.doc('rehash_post_data')
    @ns.response(200, 'Success', rehash_model)
    @ns.response(400, 'Bad request')
    def get(self, link):
        """Extract and rehash data from a provided link"""
        result = fetch_data_from_link(link)
        
        if 'error' in result:
            ns.abort(400, message="No post IDs found in the data.")
        else:
            return jsonify(result)