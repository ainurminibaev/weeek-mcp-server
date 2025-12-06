"""
HTTP Client for Weeek API.

Provides a robust HTTP client with retry logic, error handling,
and proper authentication for all Weeek API requests.
"""

import asyncio
import time
from typing import Any, Optional, Dict, Union
from pathlib import Path

import httpx

from .config import Config, get_config
from .utils.errors import (
    WeeekAPIError,
    WeeekTimeoutError,
    WeeekConnectionError,
    create_error_from_response,
)
from .utils.logger import get_logger


logger = get_logger("client")


class WeeekClient:
    """
    Async HTTP client for Weeek API with retry logic and error handling.
    
    Features:
    - Automatic Bearer token authentication
    - Retry logic for 5xx and 429 errors
    - Comprehensive error handling
    - Request/response logging (without sensitive data)
    - Support for JSON and multipart/form-data requests
    
    Example:
        >>> client = WeeekClient(token="your-token")
        >>> workspace = await client.get("/workspace")
        >>> task = await client.post("/tm/tasks", {"title": "New Task"})
    """
    
    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        retry_attempts: Optional[int] = None,
        retry_delay: Optional[float] = None,
    ):
        """
        Initialize Weeek API client.
        
        Args:
            token: Weeek API token. If not provided, uses WEEEK_TOKEN env var.
            base_url: API base URL. Defaults to https://api.weeek.net/public/v1
            timeout: Request timeout in seconds. Defaults to 30.
            retry_attempts: Number of retry attempts. Defaults to 3.
            retry_delay: Delay between retries in seconds. Defaults to 1.0.
        """
        # Load config for defaults
        try:
            config = get_config()
            self._token = token or config.weeek_token
            self._base_url = base_url or config.weeek_base_url
            self._timeout = timeout or config.request_timeout
            self._retry_attempts = retry_attempts or config.retry_attempts
            self._retry_delay = retry_delay or config.retry_delay
        except Exception:
            # If config loading fails, use provided values or defaults
            if not token:
                raise ValueError("WEEEK_TOKEN must be provided or set in environment")
            self._token = token
            self._base_url = base_url or "https://api.weeek.net/public/v1"
            self._timeout = timeout or 30
            self._retry_attempts = retry_attempts or 3
            self._retry_delay = retry_delay or 1.0
        
        # Ensure base URL doesn't have trailing slash
        self._base_url = self._base_url.rstrip("/")
        
        # Default headers for all requests
        self._headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }
        
        # HTTP client instance (created lazily)
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client instance."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=self._headers,
                timeout=httpx.Timeout(self._timeout),
            )
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client connection."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def __aenter__(self) -> "WeeekClient":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
        return endpoint
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint (e.g., "/tm/tasks")
            params: Query parameters
            json_data: JSON body data
            files: Files for multipart upload
            
        Returns:
            Parsed JSON response or empty dict for 204 responses
            
        Raises:
            WeeekAPIError: On API errors
            WeeekTimeoutError: On request timeout
            WeeekConnectionError: On connection failures
        """
        url = self._build_url(endpoint)
        client = await self._get_client()
        
        # Filter out None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}
        
        # Filter out None values from json_data
        if json_data:
            json_data = {k: v for k, v in json_data.items() if v is not None}
        
        last_error: Optional[Exception] = None
        
        for attempt in range(1, self._retry_attempts + 1):
            try:
                logger.debug(
                    f"Request: {method} {url}",
                    extra={"attempt": attempt, "params": params}
                )
                
                # Build request kwargs
                request_kwargs: Dict[str, Any] = {
                    "method": method,
                    "url": url,
                }
                
                if params:
                    request_kwargs["params"] = params
                
                if files:
                    # Multipart form data for file uploads
                    request_kwargs["files"] = files
                    if json_data:
                        request_kwargs["data"] = json_data
                elif json_data:
                    request_kwargs["json"] = json_data
                    request_kwargs["headers"] = {"Content-Type": "application/json"}
                
                response = await client.request(**request_kwargs)
                
                logger.debug(
                    f"Response: {response.status_code}",
                    extra={"status_code": response.status_code}
                )
                
                # Handle successful responses
                if response.status_code in (200, 201):
                    return response.json()
                elif response.status_code == 204:
                    return {"success": True, "message": "Operation completed successfully"}
                
                # Handle errors
                try:
                    response_body = response.json()
                except Exception:
                    response_body = response.text
                
                # Check if we should retry
                if response.status_code == 429:
                    # Rate limited - extract retry-after if available
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        wait_time = float(retry_after)
                    else:
                        wait_time = self._retry_delay * attempt
                    
                    if attempt < self._retry_attempts:
                        logger.warning(
                            f"Rate limited. Waiting {wait_time}s before retry.",
                            extra={"attempt": attempt, "wait_time": wait_time}
                        )
                        await asyncio.sleep(wait_time)
                        continue
                
                elif response.status_code >= 500:
                    # Server error - retry with exponential backoff
                    if attempt < self._retry_attempts:
                        wait_time = self._retry_delay * (2 ** (attempt - 1))
                        logger.warning(
                            f"Server error {response.status_code}. Retrying in {wait_time}s",
                            extra={"attempt": attempt, "status_code": response.status_code}
                        )
                        await asyncio.sleep(wait_time)
                        continue
                
                # Non-retryable error or max retries exceeded
                raise create_error_from_response(response.status_code, response_body)
                
            except httpx.TimeoutException as e:
                last_error = e
                if attempt < self._retry_attempts:
                    wait_time = self._retry_delay * attempt
                    logger.warning(
                        f"Request timeout. Retrying in {wait_time}s",
                        extra={"attempt": attempt}
                    )
                    await asyncio.sleep(wait_time)
                    continue
                raise WeeekTimeoutError(timeout=self._timeout)
                
            except httpx.ConnectError as e:
                last_error = e
                if attempt < self._retry_attempts:
                    wait_time = self._retry_delay * attempt
                    logger.warning(
                        f"Connection error. Retrying in {wait_time}s",
                        extra={"attempt": attempt}
                    )
                    await asyncio.sleep(wait_time)
                    continue
                raise WeeekConnectionError()
                
            except WeeekAPIError:
                raise
                
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error: {str(e)}")
                raise WeeekAPIError(f"Unexpected error: {str(e)}")
        
        # Should not reach here, but just in case
        if last_error:
            raise WeeekAPIError(f"Request failed after {self._retry_attempts} attempts: {str(last_error)}")
        raise WeeekAPIError("Request failed for unknown reason")
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Make GET request to Weeek API.
        
        Args:
            endpoint: API endpoint (e.g., "/tm/tasks")
            params: Query parameters
            
        Returns:
            Parsed JSON response
            
        Example:
            >>> tasks = await client.get("/tm/tasks", {"limit": 10, "project_id": "123"})
        """
        return await self._request("GET", endpoint, params=params)
    
    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Make POST request to Weeek API.
        
        Args:
            endpoint: API endpoint
            json_data: JSON body data
            files: Files for multipart upload
            
        Returns:
            Parsed JSON response
            
        Example:
            >>> task = await client.post("/tm/tasks", {"title": "New Task"})
        """
        return await self._request("POST", endpoint, json_data=json_data, files=files)
    
    async def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Make PUT request to Weeek API.
        
        Args:
            endpoint: API endpoint
            json_data: JSON body data
            
        Returns:
            Parsed JSON response
            
        Example:
            >>> task = await client.put("/tm/tasks/123", {"status": "completed"})
        """
        return await self._request("PUT", endpoint, json_data=json_data)
    
    async def patch(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Make PATCH request to Weeek API.
        
        Args:
            endpoint: API endpoint
            json_data: JSON body data
            
        Returns:
            Parsed JSON response
        """
        return await self._request("PATCH", endpoint, json_data=json_data)
    
    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Make DELETE request to Weeek API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters (optional)
            
        Returns:
            Success response or empty dict
            
        Example:
            >>> await client.delete("/tm/tasks/123")
        """
        return await self._request("DELETE", endpoint, params=params)


# Synchronous wrapper for compatibility
class WeeekClientSync:
    """
    Synchronous wrapper for WeeekClient.
    
    Provides blocking API for use in synchronous contexts.
    Uses asyncio.run() internally for each request.
    """
    
    def __init__(self, **kwargs):
        """Initialize with same parameters as WeeekClient."""
        self._async_client = WeeekClient(**kwargs)
    
    def _run(self, coro):
        """Run coroutine synchronously."""
        return asyncio.get_event_loop().run_until_complete(coro)
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Synchronous GET request."""
        return self._run(self._async_client.get(endpoint, params))
    
    def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Synchronous POST request."""
        return self._run(self._async_client.post(endpoint, json_data, files))
    
    def put(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
        """Synchronous PUT request."""
        return self._run(self._async_client.put(endpoint, json_data))
    
    def patch(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
        """Synchronous PATCH request."""
        return self._run(self._async_client.patch(endpoint, json_data))
    
    def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Synchronous DELETE request."""
        return self._run(self._async_client.delete(endpoint, params))
    
    def close(self) -> None:
        """Close the client."""
        self._run(self._async_client.close())

