"""
Load testing script for ListService API.

This script performs load testing on the deployed API.

Usage:
    # Option 1: Use .env file (recommended)
    # Create .env file with: API_ENDPOINT=https://cfuebpkgu1.execute-api.eu-north-1.amazonaws.com/api
    python tests/load/load_test.py --requests 1000 --concurrent 10

    # Option 2: Use environment variable
    export API_ENDPOINT="https://cfuebpkgu1.execute-api.eu-north-1.amazonaws.com/api"
    python tests/load/load_test.py --requests 1000 --concurrent 10
"""

import argparse
import os
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_ENDPOINT = os.environ.get("API_ENDPOINT")


def create_list(base_url: str, items: List[str]) -> Dict:
    """Create a list and measure response time."""
    start_time = time.time()
    try:
        response = requests.post(f"{base_url}/lists", json={"items": items}, timeout=30)
        elapsed = time.time() - start_time
        result = {
            "operation": "create",
            "status_code": response.status_code,
            "elapsed": elapsed,
            "success": response.status_code == 201,
        }
        if response.status_code == 201:
            result["list_id"] = response.json().get("list_id")
        return result
    except Exception as e:
        elapsed = time.time() - start_time
        return {"operation": "create", "status_code": 0, "elapsed": elapsed, "success": False, "error": str(e)}


def get_head(base_url: str, list_id: str, n: int = 10) -> Dict:
    """Get head of list and measure response time."""
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/lists/{list_id}/head?n={n}", timeout=30)
        elapsed = time.time() - start_time
        return {
            "operation": "head",
            "status_code": response.status_code,
            "elapsed": elapsed,
            "success": response.status_code == 200,
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {"operation": "head", "status_code": 0, "elapsed": elapsed, "success": False, "error": str(e)}


def get_tail(base_url: str, list_id: str, n: int = 10) -> Dict:
    """Get tail of list and measure response time."""
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/lists/{list_id}/tail?n={n}", timeout=30)
        elapsed = time.time() - start_time
        return {
            "operation": "tail",
            "status_code": response.status_code,
            "elapsed": elapsed,
            "success": response.status_code == 200,
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {"operation": "tail", "status_code": 0, "elapsed": elapsed, "success": False, "error": str(e)}


def run_load_test(base_url: str, num_requests: int, concurrent: int):
    """Run load test with specified parameters."""
    print(f"\n{'='*60}")
    print(f"Starting load test")
    print(f"{'='*60}")
    print(f"API Endpoint: {base_url}")
    print(f"Total Requests: {num_requests}")
    print(f"Concurrent: {concurrent}")
    print(f"{'='*60}\n")

    # Prepare test data
    test_items = [f"item-{i}" for i in range(100)]

    # First, create the test list
    print("Creating test list...")
    result = create_list(base_url, test_items)
    if not result["success"]:
        print(f"Failed to create test list: {result}")
        return

    list_id = result.get("list_id")
    if not list_id:
        print("Failed to get list_id from created list")
        return

    print(f"Test list created successfully with ID: {list_id} in {result['elapsed']:.3f}s\n")

    # Run concurrent requests
    results = []
    start_time = time.time()

    print("Running load test...")
    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = []

        for i in range(num_requests):
            # Mix of head and tail operations
            if i % 2 == 0:
                futures.append(executor.submit(get_head, base_url, list_id, 10))
            else:
                futures.append(executor.submit(get_tail, base_url, list_id, 10))

        completed = 0
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1

            if completed % 100 == 0:
                print(f"Completed: {completed}/{num_requests}")

    total_time = time.time() - start_time

    # Analyze results
    print(f"\n{'='*60}")
    print("Load Test Results")
    print(f"{'='*60}")

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"Total Requests: {len(results)}")
    print(f"Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Requests/sec: {len(results)/total_time:.2f}")

    if successful:
        response_times = [r["elapsed"] for r in successful]
        print(f"\nResponse Times (successful requests):")
        print(f"  Min: {min(response_times)*1000:.2f}ms")
        print(f"  Max: {max(response_times)*1000:.2f}ms")
        print(f"  Mean: {statistics.mean(response_times)*1000:.2f}ms")
        print(f"  Median: {statistics.median(response_times)*1000:.2f}ms")
        print(f"  P95: {sorted(response_times)[int(len(response_times)*0.95)]*1000:.2f}ms")
        print(f"  P99: {sorted(response_times)[int(len(response_times)*0.99)]*1000:.2f}ms")

    # Status code distribution
    status_codes = {}
    for r in results:
        status_codes[r["status_code"]] = status_codes.get(r["status_code"], 0) + 1

    print(f"\nStatus Code Distribution:")
    for code, count in sorted(status_codes.items()):
        print(f"  {code}: {count}")

    # Operation breakdown
    head_results = [r for r in results if r["operation"] == "head"]
    tail_results = [r for r in results if r["operation"] == "tail"]

    print(f"\nOperation Breakdown:")
    print(f"  Head: {len(head_results)} ({len([r for r in head_results if r['success']])} successful)")
    print(f"  Tail: {len(tail_results)} ({len([r for r in tail_results if r['success']])} successful)")

    print(f"\n{'='*60}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Load test ListService API")
    parser.add_argument("--requests", type=int, default=50, help="Number of requests to make (default: 100)")
    parser.add_argument("--concurrent", type=int, default=5, help="Number of concurrent requests (default: 10)")

    args = parser.parse_args()

    if not API_ENDPOINT:
        print("Error: API_ENDPOINT environment variable not set")
        print("Example: export API_ENDPOINT='https://xxxxx.execute-api.us-east-1.amazonaws.com/prod'")
        return 1

    run_load_test(API_ENDPOINT, args.requests, args.concurrent)
    return 0


if __name__ == "__main__":
    exit(main())
