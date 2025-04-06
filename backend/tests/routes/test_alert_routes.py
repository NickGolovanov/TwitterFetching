import pytest
from unittest.mock import patch, MagicMock
from src.main import app
from src.config import DYNAMODB_TABLES

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def valid_alert_data():
    return {
        "weather_type": "Storm",
        "date": "2024-03-20",
        "location": "Amsterdam",
        "map_link": "https://example.com/map"
    }

@pytest.fixture
def mock_alerts():
    return [
        {
            "weather_alert_id": 1,
            "weather_type": "Storm",
            "date_time": "2024-03-20T10:00:00",
            "location": "Amsterdam",
            "map_link": "https://example.com/map1"
        },
        {
            "weather_alert_id": 2,
            "weather_type": "Rain",
            "date_time": "2024-03-20T09:00:00",
            "location": "Rotterdam",
            "map_link": "https://example.com/map2"
        }
    ]

def test_get_alerts_success(client, mock_alerts):
    with patch('src.routes.alert.fetch_all_items') as mock_fetch:
        mock_fetch.return_value = mock_alerts

        response = client.get("/alert")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['weather_type'] == 'Storm'
        assert data[1]['weather_type'] == 'Rain'
        mock_fetch.assert_called_once_with(DYNAMODB_TABLES.get("WeatherAlert"))

def test_get_alerts_empty(client):
    with patch('src.routes.alert.fetch_all_items') as mock_fetch:
        mock_fetch.return_value = []
        
        response = client.get('/alert/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 0

def test_post_alert_success(client, valid_alert_data):
    with patch('src.routes.alert.process_weather_alert') as mock_process:
        mock_process.return_value = True
        
        response = client.post('/alert/', json=valid_alert_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Post processed'
        mock_process.assert_called_once_with(valid_alert_data)

def test_post_alert_missing_fields(client):
    invalid_data = {
        "weather_type": "Storm",
        "date": "2024-03-20"
    }
    
    response = client.post('/alert/', json=invalid_data)
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Missing required fields'

def test_post_alert_processing_error(client, valid_alert_data):
    with patch('src.routes.alert.process_weather_alert') as mock_process:
        mock_process.return_value = False
        
        response = client.post('/alert/', json=valid_alert_data)
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['message'] == 'Error processing post' 
