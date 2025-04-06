import pytest
from unittest.mock import patch, MagicMock
from src.services.post_service import fetch_data_by_post_ids, rehash_the_link, fetch_data_from_link
from cryptography.fernet import Fernet
from tests.test_config import HASHING_SECRET

@pytest.fixture
def mock_dynamodb_response():
    return {
        "Items": [
            {"post_id": 1, "content": "Test post 1"},
            {"post_id": 2, "content": "Test post 2"}
        ]
    }

@pytest.fixture
def mock_encrypted_link():
    cipher_suite = Fernet(HASHING_SECRET)
    return cipher_suite.encrypt("1,2,3".encode()).decode()

def test_fetch_data_by_post_ids_success(mock_dynamodb_response):
    with patch('src.services.post_service.dynamodb') as mock_dynamodb:
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.scan.return_value = mock_dynamodb_response
        
        result = fetch_data_by_post_ids([1, 2])
        
        assert len(result) == 2
        assert result[0]["post_id"] == 1
        assert result[1]["post_id"] == 2

def test_fetch_data_by_post_ids_empty():
    with patch('src.services.post_service.dynamodb') as mock_dynamodb:
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.scan.return_value = {"Items": []}
        
        result = fetch_data_by_post_ids([])
        
        assert result == []

def test_rehash_the_link_success(mock_encrypted_link):
    result = rehash_the_link(mock_encrypted_link)
    
    assert isinstance(result, list)
    assert "1" in result
    assert "2" in result
    assert "3" in result

def test_rehash_the_link_invalid():
    result = rehash_the_link("invalid_link")
    
    assert isinstance(result, dict)
    assert "error" in result

def test_fetch_data_from_link_success(mock_encrypted_link, mock_dynamodb_response):
    with patch('src.services.post_service.dynamodb') as mock_dynamodb:
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.scan.return_value = mock_dynamodb_response
        
        result = fetch_data_from_link(mock_encrypted_link)
        
        assert len(result) == 2
        assert result[0]["post_id"] == 1
        assert result[1]["post_id"] == 2

def test_fetch_data_from_link_invalid():
    result = fetch_data_from_link("invalid_link")
    
    assert isinstance(result, dict)
    assert "error" in result 