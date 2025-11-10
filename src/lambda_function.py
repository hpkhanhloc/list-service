"""
AWS Lambda handler for ListService REST API.
"""

import json
import traceback
from typing import Dict, Any

from list_operations import DynamoDBClient, ListService
from validators import ValidationError, validate_list_id, validate_n_parameter, validate_items, validate_request_body
from utils import (
    get_logger,
    create_response,
    create_error_response,
    parse_path_parameters,
    parse_query_parameters,
    parse_request_body,
)

logger = get_logger(__name__)

# Initialize service (reused across warm Lambda invocations)
db_client = DynamoDBClient()
list_service = ListService(db_client)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for API Gateway requests.

    Args:
        event: API Gateway event
        context: Lambda context

    Returns:
        API Gateway response
    """
    # Log request
    request_id = context.aws_request_id if context else "local"
    http_method = event.get("httpMethod", "UNKNOWN")
    resource_path = event.get("resource", "UNKNOWN")

    logger.info(f"Request started - ID: {request_id}, Method: {http_method}, Path: {resource_path}")

    try:
        # Parse parameters
        path_params = parse_path_parameters(event)
        query_params = parse_query_parameters(event)

        # Route request
        if resource_path == "/lists":
            return handle_lists_collection(event)
        elif resource_path == "/lists/{list_id}":
            return handle_list_operations(event, path_params, query_params)
        elif resource_path == "/lists/{list_id}/head":
            return handle_head_operation(path_params, query_params)
        elif resource_path == "/lists/{list_id}/tail":
            return handle_tail_operation(path_params, query_params)
        else:
            logger.warning(f"Unknown resource path: {resource_path}")
            return create_error_response(
                status_code=404, error_type="NotFound", message=f"Resource not found: {resource_path}"
            )

    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        return create_error_response(status_code=400, error_type="BadRequest", message=str(e))

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        return create_error_response(status_code=500, error_type="InternalServerError", message="An unexpected error occurred")

    finally:
        logger.info(f"Request completed - ID: {request_id}")


def handle_lists_collection(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle operations on /lists endpoint (collection).

    Args:
        event: API Gateway event

    Returns:
        API Gateway response
    """
    http_method = event.get("httpMethod")

    if http_method == "GET":
        return get_all_lists()
    elif http_method == "POST":
        return post_list(event)
    else:
        return create_error_response(
            status_code=405, error_type="MethodNotAllowed", message=f"Method {http_method} not allowed"
        )


def handle_list_operations(event: Dict[str, Any], path_params: Dict[str, str], query_params: Dict[str, str]) -> Dict[str, Any]:
    """
    Handle operations on /lists/{list_id} endpoint.

    Args:
        event: API Gateway event
        path_params: Path parameters
        query_params: Query parameters

    Returns:
        API Gateway response
    """
    http_method = event.get("httpMethod")
    list_id = validate_list_id(path_params.get("list_id", ""))

    if http_method == "GET":
        return get_list(list_id)
    elif http_method == "PUT":
        return put_list(event, list_id)
    elif http_method == "DELETE":
        return delete_list(list_id)
    else:
        return create_error_response(
            status_code=405, error_type="MethodNotAllowed", message=f"Method {http_method} not allowed"
        )


def get_list(list_id: str) -> Dict[str, Any]:
    """
    GET /lists/{list_id} - Get full list.

    Args:
        list_id: The list identifier

    Returns:
        API Gateway response
    """
    logger.info(f"Getting list: {list_id}")

    list_data = list_service.get_full_list(list_id)

    if not list_data:
        return create_error_response(status_code=404, error_type="NotFound", message=f"List '{list_id}' not found")

    return create_response(status_code=200, body=list_data)


def put_list(event: Dict[str, Any], list_id: str) -> Dict[str, Any]:
    """
    PUT /lists/{list_id} - Update existing list.

    Args:
        event: API Gateway event
        list_id: The list identifier

    Returns:
        API Gateway response
    """
    logger.info(f"Updating list: {list_id}")

    body = parse_request_body(event)
    validated_body = validate_request_body(body)
    items = validate_items(validated_body["items"])

    result = list_service.update_list(list_id, items)

    if not result:
        return create_error_response(status_code=404, error_type="NotFound", message=f"List '{list_id}' not found")

    return create_response(status_code=200, body=result)


def delete_list(list_id: str) -> Dict[str, Any]:
    """
    DELETE /lists/{list_id} - Delete list.

    Args:
        list_id: The list identifier

    Returns:
        API Gateway response
    """
    logger.info(f"Deleting list: {list_id}")

    deleted = list_service.delete_list(list_id)

    if not deleted:
        return create_error_response(status_code=404, error_type="NotFound", message=f"List '{list_id}' not found")

    return create_response(status_code=204, body={})


def get_all_lists() -> Dict[str, Any]:
    """
    GET /lists - Get all lists.

    Returns:
        API Gateway response
    """
    logger.info("Getting all lists")

    lists = list_service.get_all_lists()

    return create_response(status_code=200, body={"lists": lists, "count": len(lists)})


def post_list(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    POST /lists - Create new list with generated UUID.

    Args:
        event: API Gateway event

    Returns:
        API Gateway response
    """
    logger.info("Creating new list with generated UUID")

    body = parse_request_body(event)
    validated_body = validate_request_body(body)
    items = validate_items(validated_body["items"])

    result = list_service.create_list(items)

    return create_response(status_code=201, body=result)


def handle_head_operation(path_params: Dict[str, str], query_params: Dict[str, str]) -> Dict[str, Any]:
    """
    Handle GET /lists/{list_id}/head.

    Args:
        path_params: Path parameters
        query_params: Query parameters

    Returns:
        API Gateway response
    """
    list_id = validate_list_id(path_params.get("list_id", ""))
    n = validate_n_parameter(query_params.get("n"))

    logger.info(f"Getting head of list '{list_id}' with n={n}")

    result = list_service.get_head(list_id, n)

    if not result:
        return create_error_response(status_code=404, error_type="NotFound", message=f"List '{list_id}' not found")

    return create_response(status_code=200, body=result)


def handle_tail_operation(path_params: Dict[str, str], query_params: Dict[str, str]) -> Dict[str, Any]:
    """
    Handle GET /lists/{list_id}/tail.

    Args:
        path_params: Path parameters
        query_params: Query parameters

    Returns:
        API Gateway response
    """
    list_id = validate_list_id(path_params.get("list_id", ""))
    n = validate_n_parameter(query_params.get("n"))

    logger.info(f"Getting tail of list '{list_id}' with n={n}")

    result = list_service.get_tail(list_id, n)

    if not result:
        return create_error_response(status_code=404, error_type="NotFound", message=f"List '{list_id}' not found")

    return create_response(status_code=200, body=result)
