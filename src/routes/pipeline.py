from flask import Blueprint, jsonify
from services.pipeline_service import data_pipeline
from config import DYNAMODB_TABLES
from services.pipeline_service import collecting_data
import threading

pipeline_route = Blueprint('pipeline', __name__)

@pipeline_route.route('/start_collection', methods=["GET"])
def start_posts_collection(): 
    global collecting_data
    if not collecting_data:
        collecting_data = True
        data_thread = threading.Thread(target=data_pipeline, daemon=True)
        data_thread.start()
        return jsonify({"message": "Data collection started"}), 200
    return jsonify({"message": "Data collection started"}), 200

@pipeline_route.route('/stop_collection', methods=["GET"])
def stop_posts_collection(): 
    global collecting_data
    if not collecting_data:
        collecting_data = False
        return jsonify({"message": "Data collection stop"}), 200
    return jsonify({"message": "Data collection is not running"}), 400

@pipeline_route.route('/collection_status', methods=["GET"])
def collection_status():
    return jsonify({"collecting_data" : collecting_data}), 200