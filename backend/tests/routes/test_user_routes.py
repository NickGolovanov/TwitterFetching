import pytest
from unittest.mock import patch, MagicMock
from src.main import app
from src.config import DYNAMODB_TABLES

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def valid_user_data():
    return {
        "user_id": 1,
        "location": "Amsterdam",
        "city": "Amsterdam",
        "longitude_latitude": "52.3676° N, 4.9041° E"
    }

@pytest.fixture
def mock_users():
    return [
        {
            "user_id": 1,
            "location": "Amsterdam",
            "city": "Amsterdam",
            "longitude_latitude": "52.3676° N, 4.9041° E"
        },
        {
            "user_id": 2,
            "location": "Rotterdam",
            "city": "Rotterdam",
            "longitude_latitude": "51.9225° N, 4.4792° E"
        }
    ]

def test_get_users_success(client, mock_users):
    with patch('src.routes.user.fetch_all_items') as mock_fetch:
        mock_fetch.return_value = mock_users
        
        response = client.get('/user/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['location'] == 'Amsterdam'
        assert data[1]['location'] == 'Rotterdam'
        mock_fetch.assert_called_once_with(DYNAMODB_TABLES.get("User"))

def test_get_users_empty(client):
    with patch('src.routes.user.fetch_all_items') as mock_fetch:
        mock_fetch.return_value = []
        
        response = client.get('/user/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 0

def test_create_user_success(client, valid_user_data):
    with patch('src.routes.user.put_item') as mock_put:
        mock_put.return_value = True
        
        response = client.post('/user/', json=valid_user_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User created successfully'
        mock_put.assert_called_once_with(DYNAMODB_TABLES.get("User"), valid_user_data)

def test_create_user_missing_id(client):
    invalid_data = {
        "location": "Amsterdam",
        "city": "Amsterdam"
    }
    
    response = client.post('/user/', json=invalid_data)
    
    assert response.status_code == 400
    data = response.get_json()
    assert "Missing required 'user_id' field" in data['message']

def test_get_user_by_id_success(client, valid_user_data):
    with patch('src.routes.user.fetch_item_by_key') as mock_fetch:
        mock_fetch.return_value = valid_user_data
        
        response = client.get('/user/1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user_id'] == 1
        assert data['location'] == 'Amsterdam'
        mock_fetch.assert_called_once_with(
            DYNAMODB_TABLES.get("User"),
            "user_id",
            "1"
        )

def test_get_user_by_id_not_found(client):
    with patch('src.routes.user.fetch_item_by_key') as mock_fetch:
        mock_fetch.return_value = None
        
        response = client.get('/user/999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert "User not found" in data['message']

def test_update_user_success(client):
    update_data = {
        "location": "Utrecht",
        "city": "Utrecht"
    }
    
    with patch('src.routes.user.update_item') as mock_update:
        mock_update.return_value = True
        
        response = client.put('/user/1', json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'User updated successfully'
        mock_update.assert_called_once()

def test_update_user_no_data(client):
    response = client.put('/user/1', json={})
    
    assert response.status_code == 400
    data = response.get_json()
    assert "No update data provided" in data['message'] 