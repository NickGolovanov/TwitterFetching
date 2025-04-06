from unittest.mock import MagicMock

def insert_weather_alert(location, weather_type, date, map_link):
    return True

def retrieve_x_posts():
    return "123", [{"id": 1, "content": "Test post"}]

def process_x_posts(social_media_id, posts):
    return posts

def validate_x_posts(social_media_id, posts):
    return posts

def analyze_x_posts(social_media_id, posts):
    return posts

def store_x_posts(social_media_id, posts):
    return posts

def notify_x_posts(social_media_id, posts):
    return True

def insert_log_to_social_media(social_media_id, log):
    return True

class LogType:
    ERROR = "ERROR" 