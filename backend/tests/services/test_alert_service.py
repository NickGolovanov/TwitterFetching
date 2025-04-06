import pytest
from unittest.mock import patch, MagicMock
from src.services.alert_service import process_weather_alert

@pytest.fixture
def valid_weather_alert():
    return {
        "weather_type": "Storm",
        "date": "2024-03-20",
        "location": "Amsterdam",
        "map_link": "https://example.com/map"
    }

@pytest.fixture
def invalid_weather_alert():
    return {
        "weather_type": "Storm",
        "date": "2024-03-20"
    }

def test_process_weather_alert_success(valid_weather_alert):
    with patch('src.services.alert_service.insert_weather_alert') as mock_insert, \
         patch('src.services.alert_service.send_email') as mock_send_email:
        mock_insert.return_value = True
        mock_send_email.return_value = True
        
        result = process_weather_alert(valid_weather_alert)
        
        assert result is True
        mock_insert.assert_called_once_with(
            location="Amsterdam",
            weather_type="Storm",
            date="2024-03-20",
            map_link="https://example.com/map"
        )
        mock_send_email.assert_called_once_with(
            "Storm",
            "2024-03-20",
            "Amsterdam",
            "https://example.com/map"
        )

def test_process_weather_alert_invalid_data(invalid_weather_alert):
    with patch('src.services.alert_service.insert_weather_alert') as mock_insert, \
         patch('src.services.alert_service.send_email') as mock_send_email:
        result = process_weather_alert(invalid_weather_alert)
        
        assert result is False
        mock_insert.assert_not_called()
        mock_send_email.assert_not_called() 