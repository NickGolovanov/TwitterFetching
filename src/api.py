from flask import Flask
import boto3
from flask import jsonify  # To return a response in JSON format
from routes import main_routes

app = Flask(__name__)
app.register_blueprint(main_routes)

# Initialize DynamoDB resource, use the correct region
dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')  # Set your region here

@app.route('/')
def home():
    return '<h1>Flask Rest Api</h1>'

@app.route('/test_dynamodb')
def test():
    try:
        table = dynamodb.Table('User')
        response = table.scan() 
        
        if 'Items' in response:
            return jsonify(response['Items'])
        else:
            return jsonify({'message': 'No items found'})
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
