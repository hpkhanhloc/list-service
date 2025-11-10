"""
Unit tests for lambda_function module.
"""

import json
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from moto import mock_dynamodb

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

# Set required environment variables before importing lambda_function
os.environ["DYNAMODB_TABLE_NAME"] = "test-table"
os.environ["AWS_DEFAULT_REGION"] = "eu-north-1"


@pytest.fixture(scope="module", autouse=True)
def mock_dynamodb_module():
    """Mock DynamoDB for the entire test module."""
    with mock_dynamodb():
        yield


@pytest.fixture
def mock_context():
    """Create a mock Lambda context."""
    context = Mock()
    context.request_id = "test-request-id-123"
    context.aws_request_id = "test-request-id-123"
    return context


@pytest.fixture
def mock_list_service():
    """Create a mock list service."""
    with patch("lambda_function.list_service") as mock:
        yield mock


class TestLambdaHandler:
    """Tests for Lambda handler."""

    def test_get_list_success(self, mock_context, mock_list_service):
        """Test successful GET request."""
        from lambda_function import lambda_handler

        mock_list_service.get_full_list.return_value = {"list_id": "test-list", "items": ["a", "b", "c"], "count": 3}

        event = {
            "httpMethod": "GET",
            "resource": "/lists/{list_id}",
            "pathParameters": {"list_id": "test-list"},
            "queryStringParameters": None,
            "body": None,
        }

        response = lambda_handler(event, mock_context)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["list_id"] == "test-list"
        assert body["items"] == ["a", "b", "c"]

    def test_get_list_not_found(self, mock_context, mock_list_service):
        """Test GET request for non-existent list."""
        from lambda_function import lambda_handler

        mock_list_service.get_full_list.return_value = None

        event = {
            "httpMethod": "GET",
            "resource": "/lists/{list_id}",
            "pathParameters": {"list_id": "nonexistent"},
            "queryStringParameters": None,
            "body": None,
        }

        response = lambda_handler(event, mock_context)

        assert response["statusCode"] == 404
        body = json.loads(response["body"])
        assert body["error"] == "NotFound"

    def test_post_list_success(self, mock_context, mock_list_service):
        """Test successful POST request to create list."""
        from lambda_function import lambda_handler

        mock_list_service.create_list.return_value = {
            "list_id": "550e8400-e29b-41d4-a716-446655440000",
            "items": ["x", "y", "z"],
            "count": 3,
            "created_at": "2025-11-10T12:00:00Z",
            "updated_at": "2025-11-10T12:00:00Z",
        }

        event = {
            "httpMethod": "POST",
            "resource": "/lists",
            "pathParameters": None,
            "queryStringParameters": None,
            "body": json.dumps({"items": ["x", "y", "z"]}),
        }

        response = lambda_handler(event, mock_context)

        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert "list_id" in body
        assert body["items"] == ["x", "y", "z"]

    def test_get_all_lists_success(self, mock_context, mock_list_service):
        """Test successful GET request to list all lists."""
        from lambda_function import lambda_handler

        mock_list_service.get_all_lists.return_value = [
            {"list_id": "list-1", "items": ["a", "b"], "count": 2},
            {"list_id": "list-2", "items": ["x", "y", "z"], "count": 3},
        ]

        event = {
            "httpMethod": "GET",
            "resource": "/lists",
            "pathParameters": None,
            "queryStringParameters": None,
            "body": None,
        }

        response = lambda_handler(event, mock_context)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "lists" in body
        assert body["count"] == 2
        assert len(body["lists"]) == 2

    def test_put_list_success(self, mock_context, mock_list_service):
        """Test successful PUT request to update existing list."""
        from lambda_function import lambda_handler

        mock_list_service.update_list.return_value = {
            "list_id": "test-list",
            "items": ["x", "y", "z"],
            "count": 3,
            "created_at": "2025-11-10T12:00:00Z",
            "updated_at": "2025-11-10T12:00:00Z",
        }

        event = {
            "httpMethod": "PUT",
            "resource": "/lists/{list_id}",
            "pathParameters": {"list_id": "test-list"},
            "queryStringParameters": None,
            "body": json.dumps({"items": ["x", "y", "z"]}),
        }

        response = lambda_handler(event, mock_context)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["list_id"] == "test-list"

    def test_put_list_not_found(self, mock_context, mock_list_service):
        """Test PUT request for non-existent list."""
        from lambda_function import lambda_handler

        mock_list_service.update_list.return_value = None

        event = {
            "httpMethod": "PUT",
            "resource": "/lists/{list_id}",
            "pathParameters": {"list_id": "nonexistent"},
            "queryStringParameters": None,
            "body": json.dumps({"items": ["x", "y", "z"]}),
        }

        response = lambda_handler(event, mock_context)

        assert response["statusCode"] == 404
        body = json.loads(response["body"])
        assert body["error"] == "NotFound"

    def test_put_list_invalid_body(self, mock_context, mock_list_service):
        """Test PUT request with invalid body."""
        from lambda_function import lambda_handler

        event = {
            "httpMethod": "PUT",
            "resource": "/lists/{list_id}",
            "pathParameters": {"list_id": "test-list"},
            "queryStringParameters": None,
            "body": json.dumps({"invalid": "field"}),
        }

        response = lambda_handler(event, mock_context)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["error"] == "BadRequest"

    def test_delete_list_success(self, mock_context, mock_list_service):
        """Test successful DELETE request."""
        from lambda_function import lambda_handler

        mock_list_service.delete_list.return_value = True

        event = {
            "httpMethod": "DELETE",
            "resource": "/lists/{list_id}",
            "pathParameters": {"list_id": "test-list"},
            "queryStringParameters": None,
            "body": None,
        }

        response = lambda_handler(event, mock_context)

        assert response["statusCode"] == 204

    def test_delete_list_not_found(self, mock_context, mock_list_service):
        """Test DELETE request for non-existent list."""
        from lambda_function import lambda_handler

        mock_list_service.delete_list.return_value = False

        event = {
            "httpMethod": "DELETE",
            "resource": "/lists/{list_id}",
            "pathParameters": {"list_id": "nonexistent"},
            "queryStringParameters": None,
            "body": None,
        }

        response = lambda_handler(event, mock_context)

        assert response["statusCode"] == 404

    def test_head_operation(self, mock_context, mock_list_service):
        """Test head operation."""
        from lambda_function import lambda_handler

        mock_list_service.get_head.return_value = {
            "list_id": "test-list",
            "operation": "head",
            "items": ["a", "b"],
            "count": 2,
            "total_count": 5,
        }

        event = {
            "httpMethod": "GET",
            "resource": "/lists/{list_id}/head",
            "pathParameters": {"list_id": "test-list"},
            "queryStringParameters": {"n": "2"},
            "body": None,
        }

        response = lambda_handler(event, mock_context)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["operation"] == "head"
        assert body["count"] == 2

    def test_tail_operation(self, mock_context, mock_list_service):
        """Test tail operation."""
        from lambda_function import lambda_handler

        mock_list_service.get_tail.return_value = {
            "list_id": "test-list",
            "operation": "tail",
            "items": ["d", "e"],
            "count": 2,
            "total_count": 5,
        }

        event = {
            "httpMethod": "GET",
            "resource": "/lists/{list_id}/tail",
            "pathParameters": {"list_id": "test-list"},
            "queryStringParameters": {"n": "2"},
            "body": None,
        }

        response = lambda_handler(event, mock_context)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["operation"] == "tail"
        assert body["count"] == 2

    def test_invalid_list_id(self, mock_context, mock_list_service):
        """Test with invalid list_id."""
        from lambda_function import lambda_handler

        event = {
            "httpMethod": "GET",
            "resource": "/lists/{list_id}",
            "pathParameters": {"list_id": "invalid@id"},
            "queryStringParameters": None,
            "body": None,
        }

        response = lambda_handler(event, mock_context)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["error"] == "BadRequest"
