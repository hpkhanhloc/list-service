"""
Unit tests for validators module.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from validators import (
    ValidationError,
    validate_list_id,
    validate_n_parameter,
    validate_items,
    validate_request_body,
)


class TestValidateListId:
    """Tests for validate_list_id function."""

    def test_valid_list_id(self):
        """Test with valid list IDs."""
        assert validate_list_id("my-list") == "my-list"
        assert validate_list_id("list_123") == "list_123"
        assert validate_list_id("LIST-ABC-123") == "LIST-ABC-123"

    def test_empty_list_id(self):
        """Test with empty list ID."""
        with pytest.raises(ValidationError, match="list_id is required"):
            validate_list_id("")

    def test_too_long_list_id(self):
        """Test with list ID exceeding max length."""
        long_id = "a" * 256
        with pytest.raises(ValidationError, match="255 characters or less"):
            validate_list_id(long_id)

    def test_invalid_characters(self):
        """Test with invalid characters."""
        with pytest.raises(ValidationError, match="alphanumeric"):
            validate_list_id("list@123")

        with pytest.raises(ValidationError, match="alphanumeric"):
            validate_list_id("list 123")

        with pytest.raises(ValidationError, match="alphanumeric"):
            validate_list_id("list/123")


class TestValidateNParameter:
    """Tests for validate_n_parameter function."""

    def test_valid_n(self):
        """Test with valid n values."""
        assert validate_n_parameter("5") == 5
        assert validate_n_parameter("100") == 100
        assert validate_n_parameter("1") == 1

    def test_default_n(self):
        """Test default value when n is None."""
        assert validate_n_parameter(None) == 10
        assert validate_n_parameter(None, default=20) == 20

    def test_invalid_n_format(self):
        """Test with non-integer values."""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_n_parameter("abc")

        with pytest.raises(ValidationError, match="must be an integer"):
            validate_n_parameter("1.5")

    def test_n_too_small(self):
        """Test with n less than 1."""
        with pytest.raises(ValidationError, match="must be at least 1"):
            validate_n_parameter("0")

        with pytest.raises(ValidationError, match="must be at least 1"):
            validate_n_parameter("-5")

    def test_n_too_large(self):
        """Test with n exceeding max."""
        with pytest.raises(ValidationError, match="must be at most"):
            validate_n_parameter("101")

        with pytest.raises(ValidationError, match="must be at most"):
            validate_n_parameter("1000")


class TestValidateItems:
    """Tests for validate_items function."""

    def test_valid_items(self):
        """Test with valid item lists."""
        items = ["item1", "item2", "item3"]
        assert validate_items(items) == items

    def test_empty_items(self):
        """Test with empty items list."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_items([])

    def test_not_a_list(self):
        """Test with non-list input."""
        with pytest.raises(ValidationError, match="must be an array"):
            validate_items("not a list")

        with pytest.raises(ValidationError, match="must be an array"):
            validate_items({"items": ["a", "b"]})

    def test_non_string_items(self):
        """Test with non-string items."""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_items([1, 2, 3])

        with pytest.raises(ValidationError, match="must be a string"):
            validate_items(["valid", 123, "valid"])

    def test_item_too_long(self):
        """Test with item exceeding max length."""
        long_item = "a" * 1001
        with pytest.raises(ValidationError, match="exceeds maximum length"):
            validate_items([long_item])

    def test_too_many_items(self):
        """Test with too many items."""
        items = ["item"] * 10001
        with pytest.raises(ValidationError, match="cannot exceed 10,000"):
            validate_items(items)


class TestValidateRequestBody:
    """Tests for validate_request_body function."""

    def test_valid_body(self):
        """Test with valid request body."""
        body = {"items": ["a", "b", "c"]}
        assert validate_request_body(body) == body

    def test_none_body(self):
        """Test with None body."""
        with pytest.raises(ValidationError, match="Request body is required"):
            validate_request_body(None)

    def test_missing_items_field(self):
        """Test with missing items field."""
        with pytest.raises(ValidationError, match="must contain 'items' field"):
            validate_request_body({"other": "field"})
