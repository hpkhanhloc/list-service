"""
Integration tests for ListService API.

These tests require the infrastructure to be deployed.
Set the API_ENDPOINT environment variable before running.

Example:
    export API_ENDPOINT="https://cfuebpkgu1.execute-api.eu-north-1.amazonaws.com/api"
    pytest tests/integration/test_api.py -v

Or create a .env file in the project root with:
    API_ENDPOINT=https://cfuebpkgu1.execute-api.eu-north-1.amazonaws.com/api
"""

import os
import pytest
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_ENDPOINT = os.environ.get("API_ENDPOINT")


@pytest.fixture(scope="module")
def api_base_url():
    """Get API base URL from environment."""
    if not API_ENDPOINT:
        pytest.skip("API_ENDPOINT environment variable not set")
    return f"{API_ENDPOINT}/lists"


class TestListOperations:
    """Integration tests for list operations."""

    def test_create_and_get_list(self, api_base_url):
        """Test creating and retrieving a list."""
        # Create list with POST
        items = ["apple", "banana", "cherry"]
        response = requests.post(api_base_url, json={"items": items})

        assert response.status_code == 201
        data = response.json()
        assert "list_id" in data
        list_id = data["list_id"]
        assert data["items"] == items
        assert data["count"] == 3
        assert "created_at" in data
        assert "updated_at" in data

        # Get list
        response = requests.get(f"{api_base_url}/{list_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["list_id"] == list_id
        assert data["items"] == items

        # Cleanup
        requests.delete(f"{api_base_url}/{list_id}")

    def test_get_all_lists(self, api_base_url):
        """Test getting all lists."""
        # Create a couple of lists
        response1 = requests.post(api_base_url, json={"items": ["a", "b"]})
        list_id_1 = response1.json()["list_id"]

        response2 = requests.post(api_base_url, json={"items": ["x", "y", "z"]})
        list_id_2 = response2.json()["list_id"]

        # Get all lists
        response = requests.get(api_base_url)

        assert response.status_code == 200
        data = response.json()
        assert "lists" in data
        assert "count" in data
        assert data["count"] >= 2

        # Verify our lists are in the response
        list_ids = [lst["list_id"] for lst in data["lists"]]
        assert list_id_1 in list_ids
        assert list_id_2 in list_ids

        # Cleanup
        requests.delete(f"{api_base_url}/{list_id_1}")
        requests.delete(f"{api_base_url}/{list_id_2}")

    def test_update_list(self, api_base_url):
        """Test updating an existing list."""
        # Create list
        response = requests.post(api_base_url, json={"items": ["a", "b"]})
        list_id = response.json()["list_id"]

        # Update list
        new_items = ["x", "y", "z"]
        response = requests.put(f"{api_base_url}/{list_id}", json={"items": new_items})

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == new_items
        assert data["count"] == 3

        # Cleanup
        requests.delete(f"{api_base_url}/{list_id}")

    def test_update_nonexistent_list(self, api_base_url):
        """Test updating a list that doesn't exist."""
        response = requests.put(f"{api_base_url}/550e8400-0000-0000-0000-000000000000", json={"items": ["a", "b"]})

        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "NotFound"

    def test_head_operation(self, api_base_url):
        """Test head operation."""
        # Create list
        items = ["1", "2", "3", "4", "5"]
        response = requests.post(api_base_url, json={"items": items})
        list_id = response.json()["list_id"]

        # Get head
        response = requests.get(f"{api_base_url}/{list_id}/head?n=3")

        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "head"
        assert data["items"] == ["1", "2", "3"]
        assert data["count"] == 3
        assert data["total_count"] == 5

        # Cleanup
        requests.delete(f"{api_base_url}/{list_id}")

    def test_head_default_n(self, api_base_url):
        """Test head operation with default n."""
        # Create list with more than 10 items
        items = [str(i) for i in range(20)]
        response = requests.post(api_base_url, json={"items": items})
        list_id = response.json()["list_id"]

        # Get head without specifying n
        response = requests.get(f"{api_base_url}/{list_id}/head")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 10  # Default
        assert data["items"] == [str(i) for i in range(10)]

        # Cleanup
        requests.delete(f"{api_base_url}/{list_id}")

    def test_tail_operation(self, api_base_url):
        """Test tail operation."""
        # Create list
        items = ["1", "2", "3", "4", "5"]
        response = requests.post(api_base_url, json={"items": items})
        list_id = response.json()["list_id"]

        # Get tail
        response = requests.get(f"{api_base_url}/{list_id}/tail?n=3")

        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "tail"
        assert data["items"] == ["3", "4", "5"]
        assert data["count"] == 3
        assert data["total_count"] == 5

        # Cleanup
        requests.delete(f"{api_base_url}/{list_id}")

    def test_delete_list(self, api_base_url):
        """Test deleting a list."""
        # Create list
        response = requests.post(api_base_url, json={"items": ["a", "b"]})
        list_id = response.json()["list_id"]

        # Delete list
        response = requests.delete(f"{api_base_url}/{list_id}")
        assert response.status_code == 204

        # Verify list is gone
        response = requests.get(f"{api_base_url}/{list_id}")
        assert response.status_code == 404

    def test_get_nonexistent_list(self, api_base_url):
        """Test getting a list that doesn't exist."""
        response = requests.get(f"{api_base_url}/nonexistent-list-123")

        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "NotFound"

    def test_invalid_list_id(self, api_base_url):
        """Test with invalid list ID."""
        response = requests.put(f"{api_base_url}/invalid@id", json={"items": ["a", "b"]})

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "BadRequest"

    def test_invalid_items(self, api_base_url):
        """Test with invalid items."""
        response = requests.post(api_base_url, json={"items": []})  # Empty array

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "BadRequest"
        assert data["message"] == "items array cannot be empty"

    def test_invalid_n_parameter(self, api_base_url):
        """Test head/tail with invalid n parameter."""
        # Create list
        response = requests.post(api_base_url, json={"items": ["a", "b", "c"]})
        list_id = response.json()["list_id"]

        # Try with invalid n
        response = requests.get(f"{api_base_url}/{list_id}/head?n=abc")
        assert response.status_code == 400

        response = requests.get(f"{api_base_url}/{list_id}/head?n=0")
        assert response.status_code == 400

        response = requests.get(f"{api_base_url}/{list_id}/head?n=101")
        assert response.status_code == 400

        # Cleanup
        requests.delete(f"{api_base_url}/{list_id}")
