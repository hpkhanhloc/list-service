"""
Business logic for list operations.
"""

import os
import uuid
from typing import Dict, List, Optional, Any
import boto3
from botocore.exceptions import ClientError

from utils import get_logger, get_current_timestamp

logger = get_logger(__name__)


class DynamoDBClient:
    """Wrapper for DynamoDB operations."""

    def __init__(self):
        """Initialize DynamoDB client."""
        self.dynamodb = boto3.resource("dynamodb")
        self.table_name = os.environ.get("DYNAMODB_TABLE_NAME")
        if not self.table_name:
            raise ValueError("DYNAMODB_TABLE_NAME environment variable is required")
        self.table = self.dynamodb.Table(self.table_name)
        logger.info(f"Initialized DynamoDB client for table: {self.table_name}")

    def get_list(self, list_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a list from DynamoDB.

        Args:
            list_id: The list identifier

        Returns:
            List data or None if not found
        """
        try:
            response = self.table.get_item(Key={"list_id": list_id})
            item = response.get("Item")

            if item:
                logger.info(
                    f"Retrieved list '{list_id}' with {len(item.get('items', []))} items"
                )
            else:
                logger.info(f"List '{list_id}' not found")

            return item
        except ClientError as e:
            logger.error(f"Error getting list '{list_id}': {e}")
            raise

    def put_list(self, list_id: str, items: List[str]) -> Dict[str, Any]:
        """
        Create or update a list in DynamoDB.

        Args:
            list_id: The list identifier
            items: List of strings to store

        Returns:
            The stored list data
        """
        try:
            # Check if list exists
            existing_item = self.get_list(list_id)

            current_time = get_current_timestamp()
            item = {
                "list_id": list_id,
                "items": items,
                "count": len(items),
                "updated_at": current_time,
            }

            # Preserve created_at if updating
            if existing_item:
                item["created_at"] = existing_item.get("created_at", current_time)
                logger.info(f"Updating list '{list_id}' with {len(items)} items")
            else:
                item["created_at"] = current_time
                logger.info(f"Creating list '{list_id}' with {len(items)} items")

            self.table.put_item(Item=item)
            return item

        except ClientError as e:
            logger.error(f"Error putting list '{list_id}': {e}")
            raise

    def create_list(self, items: List[str]) -> Dict[str, Any]:
        """
        Create a new list with a generated UUID in DynamoDB.

        Args:
            items: List of strings to store

        Returns:
            The created list data
        """
        try:
            # Generate UUID for new list
            list_id = str(uuid.uuid4())

            current_time = get_current_timestamp()
            item = {
                "list_id": list_id,
                "items": items,
                "count": len(items),
                "created_at": current_time,
                "updated_at": current_time,
            }

            self.table.put_item(Item=item)
            logger.info(f"Created list '{list_id}' with {len(items)} items")
            return item

        except ClientError as e:
            logger.error(f"Error creating list: {e}")
            raise

    def update_list(self, list_id: str, items: List[str]) -> Optional[Dict[str, Any]]:
        """
        Update an existing list in DynamoDB.

        Args:
            list_id: The list identifier
            items: List of strings to store

        Returns:
            The updated list data or None if list doesn't exist
        """
        try:
            # Check if list exists
            existing_item = self.get_list(list_id)
            if not existing_item:
                return None

            current_time = get_current_timestamp()
            item = {
                "list_id": list_id,
                "items": items,
                "count": len(items),
                "created_at": existing_item.get("created_at", current_time),
                "updated_at": current_time,
            }

            self.table.put_item(Item=item)
            logger.info(f"Updated list '{list_id}' with {len(items)} items")
            return item

        except ClientError as e:
            logger.error(f"Error updating list '{list_id}': {e}")
            raise

    def get_all_lists(self) -> List[Dict[str, Any]]:
        """
        Get all lists from DynamoDB.

        Returns:
            List of all list data
        """
        try:
            response = self.table.scan()
            items = response.get("Items", [])

            logger.info(f"Retrieved {len(items)} lists")
            return items

        except ClientError as e:
            logger.error(f"Error scanning lists: {e}")
            raise

    def delete_list(self, list_id: str) -> bool:
        """
        Delete a list from DynamoDB.

        Args:
            list_id: The list identifier

        Returns:
            True if deleted, False if not found
        """
        try:
            # Check if list exists
            if not self.get_list(list_id):
                return False

            self.table.delete_item(Key={"list_id": list_id})
            logger.info(f"Deleted list '{list_id}'")
            return True

        except ClientError as e:
            logger.error(f"Error deleting list '{list_id}': {e}")
            raise


class ListService:
    """Service class for list operations."""

    def __init__(self, db_client: DynamoDBClient):
        """
        Initialize ListService.

        Args:
            db_client: DynamoDB client instance
        """
        self.db = db_client
        logger.info("Initialized ListService")

    def get_full_list(self, list_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the full list.

        Args:
            list_id: The list identifier

        Returns:
            List data or None if not found
        """
        return self.db.get_list(list_id)

    def get_head(self, list_id: str, n: int) -> Optional[Dict[str, Any]]:
        """
        Get the first n items from a list.

        Args:
            list_id: The list identifier
            n: Number of items to return

        Returns:
            Dictionary with head items or None if list not found
        """
        list_data = self.db.get_list(list_id)
        if not list_data:
            return None

        items = list_data.get("items", [])
        head_items = items[:n]

        result = {
            "list_id": list_id,
            "operation": "head",
            "items": head_items,
            "count": len(head_items),
            "total_count": len(items),
        }

        logger.info(
            f"Head operation on '{list_id}': returned {len(head_items)} of {len(items)} items"
        )
        return result

    def get_tail(self, list_id: str, n: int) -> Optional[Dict[str, Any]]:
        """
        Get the last n items from a list.

        Args:
            list_id: The list identifier
            n: Number of items to return

        Returns:
            Dictionary with tail items or None if list not found
        """
        list_data = self.db.get_list(list_id)
        if not list_data:
            return None

        items = list_data.get("items", [])
        tail_items = items[-n:] if n < len(items) else items

        result = {
            "list_id": list_id,
            "operation": "tail",
            "items": tail_items,
            "count": len(tail_items),
            "total_count": len(items),
        }

        logger.info(
            f"Tail operation on '{list_id}': returned {len(tail_items)} of {len(items)} items"
        )
        return result

    def create_list(self, items: List[str]) -> Dict[str, Any]:
        """
        Create a new list with a generated UUID.

        Args:
            items: List of strings

        Returns:
            The created list data
        """
        return self.db.create_list(items)

    def update_list(self, list_id: str, items: List[str]) -> Optional[Dict[str, Any]]:
        """
        Update an existing list.

        Args:
            list_id: The list identifier
            items: List of strings

        Returns:
            The updated list data or None if list doesn't exist
        """
        return self.db.update_list(list_id, items)

    def create_or_update_list(self, list_id: str, items: List[str]) -> Dict[str, Any]:
        """
        Create or update a list.

        Args:
            list_id: The list identifier
            items: List of strings

        Returns:
            The stored list data
        """
        return self.db.put_list(list_id, items)

    def get_all_lists(self) -> List[Dict[str, Any]]:
        """
        Get all lists.

        Returns:
            List of all list data
        """
        return self.db.get_all_lists()

    def delete_list(self, list_id: str) -> bool:
        """
        Delete a list.

        Args:
            list_id: The list identifier

        Returns:
            True if deleted, False if not found
        """
        return self.db.delete_list(list_id)
