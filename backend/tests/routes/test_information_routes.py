import pytest
from unittest.mock import patch, MagicMock
from src.main import app
from src.config import DYNAMODB_TABLES

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def valid_information_data():
    return {
        "information_id": "1",
        "geo_data_id": 1,
        "location": {"city": "Amsterdam", "coordinates": "52.3676° N, 4.9041° E"},
        "description": "Severe weather warning for Amsterdam",
        "severity": "High",
        "weather_type": "Storm",
        "date": "2024-03-20T10:00:00",
        "post_ids": [12345, 12346]
    }

@pytest.fixture
def mock_information_list():
    return [
        {
            "information_id": "1",
            "geo_data_id": 1,
            "location": {"city": "Amsterdam", "coordinates": "52.3676° N, 4.9041° E"},
            "description": "Severe weather warning for Amsterdam",
            "severity": "High",
            "weather_type": "Storm",
            "date": "2024-03-20T10:00:00",
            "post_ids": [12345, 12346]
        },
        {
            "information_id": "2",
            "geo_data_id": 2,
            "location": {"city": "Rotterdam", "coordinates": "51.9225° N, 4.4792° E"},
            "description": "Heavy rain warning for Rotterdam",
            "severity": "Medium",
            "weather_type": "Rain",
            "date": "2024-03-20T09:00:00",
            "post_ids": [12347]
        }
    ]

def test_get_information_list_success(client, mock_information_list):
    with patch('src.routes.information.fetch_all_items') as mock_fetch:
        mock_fetch.return_value = mock_information_list
        
        response = client.get('/information/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['information_id'] == '1'
        assert data[1]['information_id'] == '2'
        mock_fetch.assert_called_once_with(DYNAMODB_TABLES.get("Information"))

def test_get_information_list_empty(client):
    with patch('src.routes.information.fetch_all_items') as mock_fetch:
        mock_fetch.return_value = []
        
        response = client.get('/information/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 0

def test_create_information_success(client, valid_information_data):
    with patch('src.routes.information.put_item') as mock_put:
        mock_put.return_value = True
        
        response = client.post('/information/', json=valid_information_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Information created successfully'
        mock_put.assert_called_once_with(DYNAMODB_TABLES.get("Information"), valid_information_data)

def test_create_information_missing_id(client):
    invalid_data = {
        "geo_data_id": 1,
        "description": "Severe weather warning"
    }
    
    response = client.post('/information/', json=invalid_data)
    
    assert response.status_code == 400
    data = response.get_json()
    assert "Missing required 'information_id' field" in data['message']

def test_get_information_by_id_success(client, valid_information_data):
    with patch('src.routes.information.fetch_item_by_key') as mock_fetch:
        mock_fetch.return_value = valid_information_data
        
        response = client.get('/information/1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['information_id'] == '1'
        assert data['weather_type'] == 'Storm'
        mock_fetch.assert_called_once_with(
            DYNAMODB_TABLES.get("Information"),
            "information_id",
            "1"
        )

def test_get_information_by_id_not_found(client):
    with patch('src.routes.information.fetch_item_by_key') as mock_fetch:
        mock_fetch.return_value = None
        
        response = client.get('/information/nonexistent-id')
        
        assert response.status_code == 404
        data = response.get_json()
        assert "No information found" in data['message']

def test_update_information_success(client):
    update_data = {
        "geo_data_id": 1,
        "description": "Updated weather warning",
        "severity": "Very High",
        "post_ids": [12345, 12346, 12348]
    }
    
    with patch('src.routes.information.update_item') as mock_update:
        mock_update.return_value = True
        
        response = client.put('/information/1', json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Information updated successfully'
        mock_update.assert_called_once()

def test_update_information_no_data(client):
    response = client.put('/information/1', json={})
    
    assert response.status_code == 400
    data = response.get_json()
    assert "No update data provided" in data['message'] 