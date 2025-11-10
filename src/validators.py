"""
Input validation module for ListService.
"""

import re
from typing import Any, Dict, List, Optional, Tuple


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def validate_list_id(list_id: str) -> str:
    """
    Validate list_id parameter.

    Args:
        list_id: The list identifier

    Returns:
        Validated list_id

    Raises:
        ValidationError: If list_id is invalid
    """
    if not list_id:
        raise ValidationError("list_id is required")

    if len(list_id) > 255:
        raise ValidationError("list_id must be 255 characters or less")

    # Allow alphanumeric, hyphens, underscores
    if not re.match(r"^[a-zA-Z0-9_-]+$", list_id):
        raise ValidationError(
            "list_id must contain only alphanumeric characters, hyphens, and underscores"
        )

    return list_id


def validate_n_parameter(
    n: Optional[str], default: int = 10, max_value: int = 100
) -> int:
    """
    Validate and parse the 'n' query parameter.

    Args:
        n: The n parameter value (from query string)
        default: Default value if n is not provided
        max_value: Maximum allowed value

    Returns:
        Validated integer value

    Raises:
        ValidationError: If n is invalid
    """
    if n is None:
        return default

    try:
        n_int = int(n)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid parameter: n must be an integer, got '{n}'")

    if n_int < 1:
        raise ValidationError(f"Invalid parameter: n must be at least 1, got {n_int}")

    if n_int > max_value:
        raise ValidationError(
            f"Invalid parameter: n must be at most {max_value}, got {n_int}"
        )

    return n_int


def validate_items(items: Any) -> List[str]:
    """
    Validate items array from request body.

    Args:
        items: The items to validate

    Returns:
        Validated list of strings

    Raises:
        ValidationError: If items are invalid
    """
    if not isinstance(items, list):
        raise ValidationError("items must be an array")

    if len(items) == 0:
        raise ValidationError("items array cannot be empty")

    if len(items) > 10000:
        raise ValidationError("items array cannot exceed 10,000 elements")

    validated_items = []
    for i, item in enumerate(items):
        if not isinstance(item, str):
            raise ValidationError(
                f"items[{i}] must be a string, got {type(item).__name__}"
            )

        if len(item) > 1000:
            raise ValidationError(
                f"items[{i}] exceeds maximum length of 1000 characters"
            )

        validated_items.append(item)

    return validated_items


def validate_request_body(body: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate request body for PUT operations.

    Args:
        body: The request body

    Returns:
        Validated body

    Raises:
        ValidationError: If body is invalid
    """
    if body is None:
        raise ValidationError("Request body is required")

    if "items" not in body:
        raise ValidationError("Request body must contain 'items' field")

    return body
