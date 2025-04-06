import pytest
from unittest.mock import patch, MagicMock
from src.main import app
from src.config import DYNAMODB_TABLES

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def valid_social_media_data():
    return {
        "social_media_id": 1,
        "search_query": "weather Amsterdam storm",
        "start_time": "2024-03-20T10:00:00",
        "end_time": "2024-03-20T11:00:00",
        "logs": [
            {"timestamp": "2024-03-20T10:15:00", "action": "Search started"},
            {"timestamp": "2024-03-20T10:30:00", "action": "Found 5 posts"}
        ]
    }

@pytest.fixture
def mock_social_media_list():
    return [
        {
            "social_media_id": 1,
            "search_query": "weather Amsterdam storm",
            "start_time": "2024-03-20T10:00:00",
            "end_time": "2024-03-20T11:00:00",
            "logs": [
                {"timestamp": "2024-03-20T10:15:00", "action": "Search started"},
                {"timestamp": "2024-03-20T10:30:00", "action": "Found 5 posts"}
            ]
        },
        {
            "social_media_id": 2,
            "search_query": "weather Rotterdam rain",
            "start_time": "2024-03-20T09:00:00",
            "end_time": "2024-03-20T10:00:00",
            "logs": [
                {"timestamp": "2024-03-20T09:15:00", "action": "Search started"},
                {"timestamp": "2024-03-20T09:30:00", "action": "Found 3 posts"}
            ]
        }
    ]

def test_get_social_media_list_success(client, mock_social_media_list):
    with patch('src.routes.social_media.fetch_all_items') as mock_fetch:
        mock_fetch.return_value = mock_social_media_list
        
        response = client.get('/social_media/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['social_media_id'] == 1
        assert data[1]['social_media_id'] == 2
        mock_fetch.assert_called_once_with(DYNAMODB_TABLES.get("SocialMedia"))

def test_get_social_media_list_empty(client):
    with patch('src.routes.social_media.fetch_all_items') as mock_fetch:
        mock_fetch.return_value = []
        
        response = client.get('/social_media/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 0

def test_create_social_media_success(client, valid_social_media_data):
    with patch('src.routes.social_media.put_item') as mock_put:
        mock_put.return_value = True
        
        response = client.post('/social_media/', json=valid_social_media_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Social Media created successfully'
        mock_put.assert_called_once_with(DYNAMODB_TABLES.get("SocialMedia"), valid_social_media_data)

def test_create_social_media_missing_id(client):
    invalid_data = {
        "search_query": "weather Amsterdam storm",
        "start_time": "2024-03-20T10:00:00"
    }
    
    response = client.post('/social_media/', json=invalid_data)
    
    assert response.status_code == 400
    data = response.get_json()
    assert "Missing required 'social_media_id' field" in data['message']

def test_get_social_media_by_id_success(client, valid_social_media_data):
    with patch('src.routes.social_media.fetch_item_by_key') as mock_fetch:
        mock_fetch.return_value = valid_social_media_data
        
        response = client.get('/social_media/1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['social_media_id'] == 1
        assert data['search_query'] == 'weather Amsterdam storm'
        mock_fetch.assert_called_once_with(
            DYNAMODB_TABLES.get("SocialMedia"),
            "social_media_id",
            "1"
        )

def test_get_social_media_by_id_not_found(client):
    with patch('src.routes.social_media.fetch_item_by_key') as mock_fetch:
        mock_fetch.return_value = None
        
        response = client.get('/social_media/999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert "Social media not found" in data['message']

def test_update_social_media_success(client):
    update_data = {
        "search_query": "Updated search query",
        "end_time": "2024-03-20T12:00:00",
        "logs": [
            {"timestamp": "2024-03-20T11:00:00", "action": "Search updated"}
        ]
    }
    
    with patch('src.routes.social_media.update_item') as mock_update:
        mock_update.return_value = True
        
        response = client.put('/social_media/1', json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Social Media updated successfully'
        mock_update.assert_called_once()

def test_update_social_media_no_data(client):
    response = client.put('/social_media/1', json={})
    
    assert response.status_code == 400
    data = response.get_json()
    assert "No update data provided" in data['message'] 