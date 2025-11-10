"""
Utility functions for ListService.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        log_level = os.environ.get("LOG_LEVEL", "INFO")
        logger.setLevel(getattr(logging, log_level))

    return logger


def create_response(
    status_code: int, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Create an API Gateway response.

    Args:
        status_code: HTTP status code
        body: Response body
        headers: Optional additional headers

    Returns:
        API Gateway response dictionary
    """
    default_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET,PUT,DELETE,OPTIONS,POST",
    }

    if headers:
        default_headers.update(headers)

    return {
        "statusCode": status_code,
        "headers": default_headers,
        "body": json.dumps(body, default=str),
    }


def create_error_response(
    status_code: int, error_type: str, message: str
) -> Dict[str, Any]:
    """
    Create an error response.

    Args:
        status_code: HTTP status code
        error_type: Error type/code
        message: Error message

    Returns:
        API Gateway error response
    """
    return create_response(
        status_code=status_code, body={"error": error_type, "message": message}
    )


def get_current_timestamp() -> str:
    """
    Get current timestamp in ISO format.

    Returns:
        ISO format timestamp string
    """
    return datetime.utcnow().isoformat() + "Z"


def parse_path_parameters(event: Dict[str, Any]) -> Dict[str, str]:
    """
    Parse path parameters from API Gateway event.

    Args:
        event: API Gateway event

    Returns:
        Path parameters dictionary
    """
    return event.get("pathParameters") or {}


def parse_query_parameters(event: Dict[str, Any]) -> Dict[str, str]:
    """
    Parse query string parameters from API Gateway event.

    Args:
        event: API Gateway event

    Returns:
        Query parameters dictionary
    """
    return event.get("queryStringParameters") or {}


def parse_request_body(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parse request body from API Gateway event.

    Args:
        event: API Gateway event

    Returns:
        Parsed body dictionary or None
    """
    body = event.get("body")
    if not body:
        return None

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None
