"""
Unit tests for utils module.
"""

import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from utils import create_response, create_error_response, parse_path_parameters, parse_query_parameters, parse_request_body


class TestCreateResponse:
    """Tests for create_response function."""

    def test_basic_response(self):
        """Test creating a basic response."""
        response = create_response(200, {"message": "success"})

        assert response["statusCode"] == 200
        assert "Content-Type" in response["headers"]
        assert response["headers"]["Content-Type"] == "application/json"

        body = json.loads(response["body"])
        assert body["message"] == "success"

    def test_cors_headers(self):
        """Test CORS headers are included."""
        response = create_response(200, {})
        headers = response["headers"]

        assert "Access-Control-Allow-Origin" in headers
        assert headers["Access-Control-Allow-Origin"] == "*"

    def test_custom_headers(self):
        """Test adding custom headers."""
        custom_headers = {"X-Custom-Header": "custom-value"}
        response = create_response(200, {}, custom_headers)

        assert response["headers"]["X-Custom-Header"] == "custom-value"


class TestCreateErrorResponse:
    """Tests for create_error_response function."""

    def test_error_response(self):
        """Test creating an error response."""
        response = create_error_response(400, "BadRequest", "Invalid input")

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["error"] == "BadRequest"
        assert body["message"] == "Invalid input"


class TestParsePathParameters:
    """Tests for parse_path_parameters function."""

    def test_with_path_parameters(self):
        """Test parsing path parameters."""
        event = {"pathParameters": {"list_id": "my-list"}}
        params = parse_path_parameters(event)

        assert params["list_id"] == "my-list"

    def test_without_path_parameters(self):
        """Test with no path parameters."""
        event = {}
        params = parse_path_parameters(event)

        assert params == {}


class TestParseQueryParameters:
    """Tests for parse_query_parameters function."""

    def test_with_query_parameters(self):
        """Test parsing query parameters."""
        event = {"queryStringParameters": {"n": "5"}}
        params = parse_query_parameters(event)

        assert params["n"] == "5"

    def test_without_query_parameters(self):
        """Test with no query parameters."""
        event = {}
        params = parse_query_parameters(event)

        assert params == {}


class TestParseRequestBody:
    """Tests for parse_request_body function."""

    def test_valid_json_body(self):
        """Test parsing valid JSON body."""
        event = {"body": '{"items": ["a", "b"]}'}
        body = parse_request_body(event)

        assert body["items"] == ["a", "b"]

    def test_no_body(self):
        """Test with no body."""
        event = {}
        body = parse_request_body(event)

        assert body is None

    def test_invalid_json(self):
        """Test with invalid JSON."""
        event = {"body": "not json"}
        body = parse_request_body(event)

        assert body is None
