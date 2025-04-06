from src.database.models.weather_alert import insert_weather_alert
from src.services.email_service import send_email


def process_weather_alert(post_data):
    """Processes a weather-related post, saves it to DynamoDB, and sends an email."""

    weather_type = post_data.get("weather_type")
    date = post_data.get("date")
    location = post_data.get("location")
    map_link = post_data.get("map_link")

    if not all([weather_type, date, location, map_link]):
        print("❌ Incomplete weather alert data, skipping...")
        return False

    insert_weather_alert(
        location=location, weather_type=weather_type, date=date, map_link=map_link
    )
    # Send an email notification
    send_email(weather_type, date, location, map_link)

    return True
