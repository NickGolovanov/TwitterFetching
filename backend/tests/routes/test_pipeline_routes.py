import pytest
from unittest.mock import patch, MagicMock
from src.main import app
import threading

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_start_collection_success(client):
    with patch('src.routes.pipeline.data_thread', None), \
         patch('src.routes.pipeline.threading.Thread') as mock_thread:
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        response = client.get('/pipeline/start_collection')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Data collection started'
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

def test_start_collection_already_running(client):
    mock_thread = MagicMock()
    mock_thread.is_alive.return_value = True
    
    with patch('src.routes.pipeline.data_thread', mock_thread):
        response = client.get('/pipeline/start_collection')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Data collection already started'

def test_stop_collection_success(client):
    mock_thread = MagicMock()
    mock_thread.is_alive.return_value = True
    
    with patch('src.routes.pipeline.data_thread', mock_thread), \
         patch('src.routes.pipeline.collecting_data') as mock_collecting_data:
        
        response = client.get('/pipeline/stop_collection')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Data collection stopped'
        mock_collecting_data.set.assert_called_once()
        mock_thread.join.assert_called_once()

def test_stop_collection_not_running(client):
    with patch('src.routes.pipeline.data_thread', None):
        response = client.get('/pipeline/stop_collection')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['message'] == 'Data collection is not running'

def test_collection_status_running(client):
    mock_thread = MagicMock()
    mock_thread.is_alive.return_value = True
    
    with patch('src.routes.pipeline.data_thread', mock_thread):
        response = client.get('/pipeline/collection_status')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['collecting_data'] is True

def test_collection_status_not_running(client):
    with patch('src.routes.pipeline.data_thread', None):
        response = client.get('/pipeline/collection_status')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['collecting_data'] is False 