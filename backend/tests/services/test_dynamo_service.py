import pytest
from unittest.mock import patch, MagicMock
from src.services.dynamo_service import (
    fetch_all_items,
    fetch_item_by_key,
    put_item,
    update_item,
)
from mock_database import dynamodb


@pytest.fixture
def mock_items():
    return [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]


@pytest.fixture
def mock_item():
    return {"id": 1, "name": "Item 1"}


def test_fetch_all_items_success(mock_items):
    with patch("src.services.dynamo_service.dynamodb") as mock_dynamodb:
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.scan.return_value = {"Items": mock_items}

        result = fetch_all_items("TestTable")

        assert result == mock_items
        mock_table.scan.assert_called_once()


def test_fetch_all_items_empty():
    with patch("src.services.dynamo_service.dynamodb") as mock_dynamodb:
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.scan.return_value = {"Items": []}

        result = fetch_all_items("TestTable")

        assert result == []


def test_fetch_all_items_error():
    with patch("src.services.dynamo_service.dynamodb") as mock_dynamodb:
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.scan.side_effect = Exception("Test error")

        result = fetch_all_items("TestTable")

        assert result is None


def test_fetch_item_by_key_success(mock_items):
    with patch("src.services.dynamo_service.dynamodb") as mock_dynamodb:
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.query.return_value = {"Items": mock_items}

        result = fetch_item_by_key("TestTable", "id", 1)

        assert result == mock_items
        mock_table.query.assert_called_once()


def test_fetch_item_by_key_empty():
    with patch("src.services.dynamo_service.dynamodb") as mock_dynamodb:
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.query.return_value = {"Items": []}

        result = fetch_item_by_key("TestTable", "id", 1)

        assert result == []


def test_fetch_item_by_key_error():
    with patch("src.services.dynamo_service.dynamodb") as mock_dynamodb:
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.query.side_effect = Exception("Test error")

        result = fetch_item_by_key("TestTable", "id", 1)

        assert result == []


def test_put_item_success(mock_item):
    with patch("src.services.dynamo_service.dynamodb") as mock_dynamodb:
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        result = put_item("TestTable", mock_item)

        assert result is not None
        mock_table.put_item.assert_called_once_with(Item=mock_item)


def test_put_item_error(mock_item):
    with patch("src.services.dynamo_service.dynamodb") as mock_dynamodb:
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.put_item.side_effect = Exception("Test error")

        result = put_item("TestTable", mock_item)

        assert result is None


def test_update_item_success():
    with patch("src.services.dynamo_service.dynamodb") as mock_dynamodb:
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.update_item.return_value = {"Attributes": {"name": "Updated Item"}}

        result = update_item(
            "TestTable",
            {"id": 1},
            "SET name = :name",
            {":name": "Updated Item"},
            {"#name": "name"},
        )

        assert result is not None
        mock_table.update_item.assert_called_once()


def test_update_item_error():
    with patch("src.services.dynamo_service.dynamodb") as mock_dynamodb:
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.update_item.side_effect = Exception("Test error")

        result = update_item(
            "TestTable",
            {"id": 1},
            "SET name = :name",
            {":name": "Updated Item"},
            {"#name": "name"},
        )

        assert result is None
