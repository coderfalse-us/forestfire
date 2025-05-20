"""Mock utilities for API testing."""

from unittest.mock import MagicMock
import httpx


class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text

    def json(self):
        """Return JSON data."""
        return self._json_data

    def raise_for_status(self):
        """Raise an exception if status code indicates an error."""
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP Error {self.status_code}",
                request=MagicMock(),
                response=self,
            )


class MockAsyncClient:
    """Mock async HTTP client for testing."""

    def __init__(self, verify=True):
        self.verify = verify
        self.requests = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def put(self, url, json=None, headers=None, timeout=None):
        """Mock PUT request."""
        self.requests.append(
            {
                "method": "PUT",
                "url": url,
                "json": json,
                "headers": headers,
                "timeout": timeout,
            }
        )

        # Check if we should simulate an error
        if getattr(self, "simulate_error", False):
            raise httpx.RequestError("Connection error", request=MagicMock())

        if getattr(self, "simulate_http_error", False):
            return MockResponse(status_code=500, text="Internal Server Error")

        # Return a successful response
        return MockResponse(
            status_code=200,
            json_data={
                "status": "success",
                "message": "Pick sequences updated successfully",
            },
            text="Success",
        )

    async def post(self, url, json=None, headers=None, timeout=None):
        """Mock POST request."""
        self.requests.append(
            {
                "method": "POST",
                "url": url,
                "json": json,
                "headers": headers,
                "timeout": timeout,
            }
        )

        # Check if we should simulate an error
        if getattr(self, "simulate_error", False):
            raise httpx.RequestError("Connection error", request=MagicMock())

        if getattr(self, "simulate_http_error", False):
            return MockResponse(status_code=500, text="Internal Server Error")

        # Return a successful response
        return MockResponse(
            status_code=200,
            json_data={
                "status": "success",
                "message": "Data processed successfully",
            },
            text="Success",
        )

    async def get(self, url, headers=None, timeout=None):
        """Mock GET request."""
        self.requests.append(
            {
                "method": "GET",
                "url": url,
                "headers": headers,
                "timeout": timeout,
            }
        )

        # Check if we should simulate an error
        if getattr(self, "simulate_error", False):
            raise httpx.RequestError("Connection error", request=MagicMock())

        if getattr(self, "simulate_http_error", False):
            return MockResponse(status_code=500, text="Internal Server Error")

        # Return a successful response
        return MockResponse(
            status_code=200,
            json_data={"status": "success", "data": {"key": "value"}},
            text="Success",
        )


def mock_httpx_client(simulate_error=False, simulate_http_error=False):
    """Create a mock HTTPX client with specified behavior."""
    client = MockAsyncClient()
    client.simulate_error = simulate_error
    client.simulate_http_error = simulate_http_error
    return client
