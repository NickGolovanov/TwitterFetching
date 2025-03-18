from flask import Flask
import boto3
from flask_restx import Api, Resource, fields
import threading
from services.pipeline_service import data_pipeline

# Import namespaces
from routes.geo_data import ns as geo_data_ns
from routes.information import ns as information_ns
from routes.user import ns as user_ns
from routes.social_media import ns as social_media_ns
from routes.post import ns as post_ns
from routes.pipeline import ns as pipeline_ns

# Initialize Flask app
app = Flask(__name__)

# Initialize Swagger documentation
api = Api(app, 
    version='1.0', 
    title='Weather Project API',
    description='A REST API for weather data and related services',
    doc='/swagger',
    default='main',
    default_label='Main Operations'
)

# Register namespaces
api.add_namespace(geo_data_ns, path='/geo_data')
api.add_namespace(information_ns, path='/information')
api.add_namespace(user_ns, path='/user')
api.add_namespace(social_media_ns, path='/social_media')
api.add_namespace(post_ns, path='/post')
api.add_namespace(pipeline_ns, path='/pipeline')

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb", region_name="eu-north-1")

# Define models for root endpoints
dynamodb_response_model = api.model('DynamoDBResponse', {
    'Items': fields.List(fields.Raw, description='DynamoDB items'),
    'message': fields.String(description='Response message when no items found')
})

@api.route('/')
class Home(Resource):
    @api.doc('home')
    def get(self):
        """Home endpoint returning a welcome message"""
        return "<h1>Flask Rest API</h1>"

@api.route('/test_dynamodb')
class TestDynamoDB(Resource):
    @api.doc('test_dynamodb')
    @api.response(200, 'Success', dynamodb_response_model)
    @api.response(500, 'Server Error')
    def get(self):
        """Test DynamoDB connection"""
        try:
            table = dynamodb.Table("User")
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
    app.run(debug=True, port=5001)