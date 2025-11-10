"""
Unit tests for list_operations module.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from list_operations import ListService


class TestListService:
    """Tests for ListService class."""

    @pytest.fixture
    def mock_db_client(self):
        """Create a mock DynamoDB client."""
        mock_client = Mock()
        return mock_client

    @pytest.fixture
    def list_service(self, mock_db_client):
        """Create a ListService instance with mock DB client."""
        return ListService(mock_db_client)

    def test_get_full_list_found(self, list_service, mock_db_client):
        """Test getting a list that exists."""
        mock_db_client.get_list.return_value = {
            "list_id": "test-list",
            "items": ["a", "b", "c"],
            "count": 3,
        }

        result = list_service.get_full_list("test-list")

        assert result is not None
        assert result["list_id"] == "test-list"
        assert result["items"] == ["a", "b", "c"]
        mock_db_client.get_list.assert_called_once_with("test-list")

    def test_get_full_list_not_found(self, list_service, mock_db_client):
        """Test getting a list that doesn't exist."""
        mock_db_client.get_list.return_value = None

        result = list_service.get_full_list("nonexistent")

        assert result is None
        mock_db_client.get_list.assert_called_once_with("nonexistent")

    def test_get_head(self, list_service, mock_db_client):
        """Test head operation."""
        mock_db_client.get_list.return_value = {
            "list_id": "test-list",
            "items": ["a", "b", "c", "d", "e"],
            "count": 5,
        }

        result = list_service.get_head("test-list", 3)

        assert result is not None
        assert result["list_id"] == "test-list"
        assert result["operation"] == "head"
        assert result["items"] == ["a", "b", "c"]
        assert result["count"] == 3
        assert result["total_count"] == 5

    def test_get_head_n_larger_than_list(self, list_service, mock_db_client):
        """Test head operation when n is larger than list size."""
        mock_db_client.get_list.return_value = {
            "list_id": "test-list",
            "items": ["a", "b"],
            "count": 2,
        }

        result = list_service.get_head("test-list", 10)

        assert result is not None
        assert result["items"] == ["a", "b"]
        assert result["count"] == 2
        assert result["total_count"] == 2

    def test_get_head_list_not_found(self, list_service, mock_db_client):
        """Test head operation on non-existent list."""
        mock_db_client.get_list.return_value = None

        result = list_service.get_head("nonexistent", 3)

        assert result is None

    def test_get_tail(self, list_service, mock_db_client):
        """Test tail operation."""
        mock_db_client.get_list.return_value = {
            "list_id": "test-list",
            "items": ["a", "b", "c", "d", "e"],
            "count": 5,
        }

        result = list_service.get_tail("test-list", 3)

        assert result is not None
        assert result["list_id"] == "test-list"
        assert result["operation"] == "tail"
        assert result["items"] == ["c", "d", "e"]
        assert result["count"] == 3
        assert result["total_count"] == 5

    def test_get_tail_n_larger_than_list(self, list_service, mock_db_client):
        """Test tail operation when n is larger than list size."""
        mock_db_client.get_list.return_value = {
            "list_id": "test-list",
            "items": ["a", "b"],
            "count": 2,
        }

        result = list_service.get_tail("test-list", 10)

        assert result is not None
        assert result["items"] == ["a", "b"]
        assert result["count"] == 2
        assert result["total_count"] == 2

    def test_get_tail_list_not_found(self, list_service, mock_db_client):
        """Test tail operation on non-existent list."""
        mock_db_client.get_list.return_value = None

        result = list_service.get_tail("nonexistent", 3)

        assert result is None

    def test_create_list(self, list_service, mock_db_client):
        """Test creating a new list with UUID."""
        expected_result = {
            "list_id": "550e8400-e29b-41d4-a716-446655440000",
            "items": ["x", "y", "z"],
            "count": 3,
            "created_at": "2025-11-10T12:00:00Z",
            "updated_at": "2025-11-10T12:00:00Z",
        }
        mock_db_client.create_list.return_value = expected_result

        result = list_service.create_list(["x", "y", "z"])

        assert result == expected_result
        mock_db_client.create_list.assert_called_once_with(["x", "y", "z"])

    def test_update_list_success(self, list_service, mock_db_client):
        """Test updating an existing list."""
        expected_result = {
            "list_id": "test-list",
            "items": ["x", "y", "z"],
            "count": 3,
            "created_at": "2025-11-10T12:00:00Z",
            "updated_at": "2025-11-10T12:05:00Z",
        }
        mock_db_client.update_list.return_value = expected_result

        result = list_service.update_list("test-list", ["x", "y", "z"])

        assert result == expected_result
        mock_db_client.update_list.assert_called_once_with("test-list", ["x", "y", "z"])

    def test_update_list_not_found(self, list_service, mock_db_client):
        """Test updating a list that doesn't exist."""
        mock_db_client.update_list.return_value = None

        result = list_service.update_list("nonexistent", ["x", "y", "z"])

        assert result is None
        mock_db_client.update_list.assert_called_once_with(
            "nonexistent", ["x", "y", "z"]
        )

    def test_get_all_lists(self, list_service, mock_db_client):
        """Test getting all lists."""
        expected_result = [
            {"list_id": "list-1", "items": ["a", "b"], "count": 2},
            {"list_id": "list-2", "items": ["x", "y", "z"], "count": 3},
        ]
        mock_db_client.get_all_lists.return_value = expected_result

        result = list_service.get_all_lists()

        assert result == expected_result
        assert len(result) == 2
        mock_db_client.get_all_lists.assert_called_once()

    def test_create_or_update_list(self, list_service, mock_db_client):
        """Test creating/updating a list (legacy method)."""
        expected_result = {
            "list_id": "test-list",
            "items": ["x", "y", "z"],
            "count": 3,
            "created_at": "2025-11-10T12:00:00Z",
            "updated_at": "2025-11-10T12:00:00Z",
        }
        mock_db_client.put_list.return_value = expected_result

        result = list_service.create_or_update_list("test-list", ["x", "y", "z"])

        assert result == expected_result
        mock_db_client.put_list.assert_called_once_with("test-list", ["x", "y", "z"])

    def test_delete_list_success(self, list_service, mock_db_client):
        """Test deleting a list that exists."""
        mock_db_client.delete_list.return_value = True

        result = list_service.delete_list("test-list")

        assert result is True
        mock_db_client.delete_list.assert_called_once_with("test-list")

    def test_delete_list_not_found(self, list_service, mock_db_client):
        """Test deleting a list that doesn't exist."""
        mock_db_client.delete_list.return_value = False

        result = list_service.delete_list("nonexistent")

        assert result is False
        mock_db_client.delete_list.assert_called_once_with("nonexistent")
