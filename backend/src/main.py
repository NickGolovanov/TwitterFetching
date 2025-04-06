from flask import Flask
import boto3
from flask_restx import Api, Resource, fields
import threading
from flask_cors import CORS
from src.database.db import (
    create_main_tables_if_not_exist,
    dynamodb_client,
    dynamodb_resource,
)
from src.routes.user import user_model

from src.routes import (
    geo_data_ns,
    information_ns,
    user_ns,
    social_media_ns,
    post_ns,
    pipeline_ns,
    alert_ns,
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

api = Api(
    app,
    version="1.0",
    title="Weather Project API",
    description="A REST API for weather data and related services",
    doc="/swagger",
    default="main",
    default_label="Main Operations",
)

api.add_namespace(geo_data_ns, path="/geo_data")
api.add_namespace(information_ns, path="/information")
api.add_namespace(user_ns, path="/user")
api.add_namespace(social_media_ns, path="/social_media")
api.add_namespace(post_ns, path="/post")
api.add_namespace(pipeline_ns, path="/pipeline")
api.add_namespace(alert_ns, path="/alert")


@api.route("/")
class Home(Resource):
    @api.doc("home")
    def get(self):
        """Home endpoint returning a welcome message"""
        return "<h1>Flask Rest API</h1>"


@api.route("/test_dynamodb")
class TestDynamoDB(Resource):
    @api.doc("test_dynamodb")
    @api.response(200, "Success", [user_model])
    @api.response(500, "Server Error")
    def get(self):
        """Test DynamoDB connection"""
        try:
            table = dynamodb_resource.Table("User")
            response = table.scan()
            if "Items" in response:
                return response["Items"]
            else:
                return {"message": "No items found"}
        except Exception as e:
            return {"error": str(e)}, 500


if __name__ == "__main__":
    # Uncomment to start data pipeline on application start
    # data_thread = threading.Thread(target=data_pipeline, daemon=True)
    # data_thread.start()

    create_main_tables_if_not_exist(dynamodb_client)

    app.run(debug=True, port=5001)
