from flask import Flask
import boto3
from flask import jsonify  # To return a response in JSON format

app = Flask(__name__)

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
            print("stage")
            return jsonify({'message': 'No items found'})
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
