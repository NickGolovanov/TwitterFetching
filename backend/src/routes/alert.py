from flask import request
from flask_restx import Namespace, Resource, fields
from src.services.alert_service import process_weather_alert
from src.services.dynamo_service import fetch_all_items
from src.config import DYNAMODB_TABLES

# Create namespace
ns = Namespace("alert", description="Weather alert processing operations")

# Define models for documentation
alert_model = ns.model(
    "WeatherAlert",
    {
        "weather_type": fields.String(
            required=True, description="Type of weather event"
        ),
        "date": fields.String(required=True, description="Datetime of the event"),
        "location": fields.String(required=True, description="Location of the event"),
        "map_link": fields.String(required=True, description="Link to the map"),
    },
)

message_model = ns.model(
    "Message", {"message": fields.String(required=True, description="Status message")}
)


@ns.route("/")
class GetAlerts(Resource):
    @ns.doc("get_alerts")
    @ns.response(200, "Success", [alert_model])
    def get(self):
        """Fetches latest weather alerts for the Chrome extension."""
        alerts = fetch_all_items(DYNAMODB_TABLES.get("WeatherAlert"))
        if not alerts:
            return [], 200

        # Convert Decimal objects to int or float for JSON serialization
        for alert in alerts:
            alert["weather_alert_id"] = int(alert["weather_alert_id"])

        alerts = sorted(alerts, key=lambda x: x["date"], reverse=True)
        return alerts, 200

    @ns.expect(alert_model)
    @ns.response(200, "Post processed", message_model)
    @ns.response(400, "Missing required fields", message_model)
    @ns.response(500, "Error processing post", message_model)
    def post(self):
        """Receives and processes a weather-related post"""
        data = request.json

        required_fields = ["weather_type", "date", "location", "map_link"]
        if not all(field in data for field in required_fields):
            return {"message": "Missing required fields"}, 400

        success = process_weather_alert(data)
        return {"message": "Post processed" if success else "Error processing post"}, (
            200 if success else 500
        )
