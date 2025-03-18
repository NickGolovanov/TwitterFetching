from flask import jsonify
from flask_restx import Namespace, Resource, fields
from services.pipeline_service import data_pipeline
from config import DYNAMODB_TABLES
from services.pipeline_service import collecting_data
import threading

# Create namespace
ns = Namespace('pipeline', description='Pipeline operations for data collection')

# Define models for documentation
status_model = ns.model('CollectionStatus', {
    'collecting_data': fields.Boolean(required=True, description='Current data collection status')
})

message_model = ns.model('Message', {
    'message': fields.String(required=True, description='Status message')
})

@ns.route('/start_collection')
class StartCollection(Resource):
    @ns.doc('start_posts_collection')
    @ns.response(200, 'Collection started', message_model)
    def get(self):
        """Start data collection pipeline"""
        global collecting_data
        if not collecting_data:
            collecting_data = True
            data_thread = threading.Thread(target=data_pipeline, daemon=True)
            data_thread.start()
            return {"message": "Data collection started"}, 200
        return {"message": "Data collection already started"}, 200

@ns.route('/stop_collection')
class StopCollection(Resource):
    @ns.doc('stop_posts_collection')
    @ns.response(200, 'Collection stopped', message_model)
    @ns.response(400, 'Collection not running', message_model)
    def get(self):
        """Stop data collection pipeline"""
        global collecting_data
        if collecting_data:
            collecting_data = False
            return {"message": "Data collection stopped"}, 200
        return {"message": "Data collection is not running"}, 400

@ns.route('/collection_status')
class CollectionStatus(Resource):
    @ns.doc('collection_status')
    @ns.response(200, 'Success', status_model)
    def get(self):
        """Get current data collection status"""
        return {"collecting_data": collecting_data}, 200