import pytest
from unittest.mock import patch, MagicMock
from src.main import app
from src.config import DYNAMODB_TABLES

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def valid_post_data():
    return {
        "post_id": "1",
        "social_media_id": 1,
        "location": {"city": "Amsterdam", "coordinates": "52.3676° N, 4.9041° E"},
        "description": "Heavy storm in Amsterdam",
        "severity": "High",
        "weather_type": "Storm",
        "date": "2024-03-20T10:00:00",
        "id": 12345
    }

@pytest.fixture
def mock_posts():
    return [
        {
            "post_id": "1",
            "social_media_id": 1,
            "location": {"city": "Amsterdam", "coordinates": "52.3676° N, 4.9041° E"},
            "description": "Heavy storm in Amsterdam",
            "severity": "High",
            "weather_type": "Storm",
            "date": "2024-03-20T10:00:00",
            "id": 12345
        },
        {
            "post_id": "2",
            "social_media_id": 2,
            "location": {"city": "Rotterdam", "coordinates": "51.9225° N, 4.4792° E"},
            "description": "Heavy rain in Rotterdam",
            "severity": "Medium",
            "weather_type": "Rain",
            "date": "2024-03-20T09:00:00",
            "id": 12346
        }
    ]

def test_get_posts_success(client, mock_posts):
    with patch('src.routes.post.fetch_all_items') as mock_fetch:
        mock_fetch.return_value = mock_posts
        
        response = client.get('/post/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['post_id'] == '1'
        assert data[1]['post_id'] == '2'
        # Verify posts are sorted by date in descending order
        assert data[0]['date'] > data[1]['date']
        mock_fetch.assert_called_once_with(DYNAMODB_TABLES.get("Post"))

def test_get_posts_empty(client):
    with patch('src.routes.post.fetch_all_items') as mock_fetch:
        mock_fetch.return_value = []
        
        response = client.get('/post/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 0

def test_create_post_success(client, valid_post_data):
    with patch('src.routes.post.put_item') as mock_put:
        mock_put.return_value = True
        
        response = client.post('/post/', json=valid_post_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Post created successfully'
        mock_put.assert_called_once_with(DYNAMODB_TABLES.get("Post"), valid_post_data)

def test_create_post_missing_id(client):
    invalid_data = {
        "social_media_id": 1,
        "description": "Heavy storm in Amsterdam"
    }
    
    response = client.post('/post/', json=invalid_data)
    
    assert response.status_code == 400
    data = response.get_json()
    assert "Missing required 'post_id' field" in data['message']

def test_get_post_by_id_success(client, valid_post_data):
    with patch('src.routes.post.fetch_item_by_key') as mock_fetch:
        mock_fetch.return_value = valid_post_data
        
        response = client.get('/post/1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['post_id'] == '1'
        assert data['weather_type'] == 'Storm'
        mock_fetch.assert_called_once_with(
            DYNAMODB_TABLES.get("Post"),
            "post_id",
            "1"
        )

def test_get_post_by_id_not_found(client):
    with patch('src.routes.post.fetch_item_by_key') as mock_fetch:
        mock_fetch.return_value = None
        
        response = client.get('/post/nonexistent-post')
        
        assert response.status_code == 404
        data = response.get_json()
        assert "No post found" in data['message']

def test_update_post_success(client):
    update_data = {
        "social_media_id": 1,
        "description": "Updated storm description",
        "severity": "Very High"
    }
    
    with patch('src.routes.post.update_item') as mock_update:
        mock_update.return_value = True
        
        response = client.put('/post/1', json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Post updated successfully'
        mock_update.assert_called_once()

def test_update_post_no_data(client):
    response = client.put('/post/1', json={})
    
    assert response.status_code == 400
    data = response.get_json()
    assert "No update data provided" in data['message'] 