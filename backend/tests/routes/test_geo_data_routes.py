import pytest
from unittest.mock import patch, MagicMock
from src.main import app
from src.config import DYNAMODB_TABLES

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def valid_geo_data():
    return {
        "geo_data_id": 1,
        "search_query": "Amsterdam weather",
        "start_time": "2024-03-20T10:00:00",
        "end_time": "2024-03-20T11:00:00"
    }

@pytest.fixture
def mock_geo_data_list():
    return [
        {
            "geo_data_id": 1,
            "search_query": "Amsterdam weather",
            "start_time": "2024-03-20T10:00:00",
            "end_time": "2024-03-20T11:00:00"
        },
        {
            "geo_data_id": 2,
            "search_query": "Rotterdam weather",
            "start_time": "2024-03-20T09:00:00",
            "end_time": "2024-03-20T10:00:00"
        }
    ]

def test_get_geo_data_list_success(client, mock_geo_data_list):
    with patch('src.routes.geo_data.fetch_all_items') as mock_fetch:
        mock_fetch.return_value = mock_geo_data_list
        
        response = client.get('/geo_data/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['geo_data_id'] == 1
        assert data[1]['geo_data_id'] == 2
        mock_fetch.assert_called_once_with(DYNAMODB_TABLES.get("GeoData"))

def test_get_geo_data_list_empty(client):
    with patch('src.routes.geo_data.fetch_all_items') as mock_fetch:
        mock_fetch.return_value = []
        
        response = client.get('/geo_data/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 0

def test_create_geo_data_success(client, valid_geo_data):
    with patch('src.routes.geo_data.put_item') as mock_put:
        mock_put.return_value = True
        
        response = client.post('/geo_data/', json=valid_geo_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'GeoData created successfully'
        mock_put.assert_called_once_with(DYNAMODB_TABLES.get("GeoData"), valid_geo_data)

def test_create_geo_data_missing_id(client):
    invalid_data = {
        "search_query": "Amsterdam weather",
        "start_time": "2024-03-20T10:00:00"
    }
    
    response = client.post('/geo_data/', json=invalid_data)
    
    assert response.status_code == 400
    data = response.get_json()
    assert "Missing required 'geo_data_id' field" in data['message']

def test_get_geo_data_by_id_success(client, valid_geo_data):
    with patch('src.routes.geo_data.fetch_item_by_key') as mock_fetch:
        mock_fetch.return_value = valid_geo_data
        
        response = client.get('/geo_data/1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['geo_data_id'] == 1
        mock_fetch.assert_called_once_with(
            DYNAMODB_TABLES.get("GeoData"),
            "geo_data_id",
            "1"
        )

def test_get_geo_data_by_id_not_found(client):
    with patch('src.routes.geo_data.fetch_item_by_key') as mock_fetch:
        mock_fetch.return_value = None
        
        response = client.get('/geo_data/nonexistent-id')
        
        assert response.status_code == 404
        data = response.get_json()
        assert "No geo data found" in data['message']

def test_update_geo_data_success(client):
    update_data = {
        "search_query": "Updated query",
        "end_time": "2024-03-20T12:00:00"
    }
    
    with patch('src.routes.geo_data.update_item') as mock_update:
        mock_update.return_value = True
        
        response = client.put('/geo_data/1', json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'GeoData updated successfully'
        mock_update.assert_called_once()

def test_update_geo_data_no_data(client):
    response = client.put('/geo_data/1', json={})
    
    assert response.status_code == 400
    data = response.get_json()
    assert "No update data provided" in data['message'] 