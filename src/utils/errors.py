"""
Custom exception classes for Weeek API errors.

Provides structured error handling with meaningful messages for different
HTTP status codes and error scenarios.
"""

from typing import Optional, Any


class WeeekAPIError(Exception):
    """
    Base exception for all Weeek API errors.
    
    Attributes:
        message: Human-readable error message
        status_code: HTTP status code (if applicable)
        response_body: Raw response body from API
    """
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Convert error to dictionary for JSON serialization."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "status_code": self.status_code,
        }


class WeeekAuthError(WeeekAPIError):
    """
    Authentication error (HTTP 401).
    
    Raised when the API token is invalid, expired, or missing.
    """
    
    def __init__(
        self,
        message: str = "Invalid or expired Weeek token. Please check WEEEK_TOKEN environment variable.",
        response_body: Optional[Any] = None
    ):
        super().__init__(message, status_code=401, response_body=response_body)


class WeeekForbiddenError(WeeekAPIError):
    """
    Authorization error (HTTP 403).
    
    Raised when the user doesn't have permission to access the resource.
    """
    
    def __init__(
        self,
        message: str = "Access denied. Check your token permissions in Weeek workspace settings.",
        response_body: Optional[Any] = None
    ):
        super().__init__(message, status_code=403, response_body=response_body)


class WeeekNotFoundError(WeeekAPIError):
    """
    Resource not found error (HTTP 404).
    
    Raised when the requested resource doesn't exist.
    """
    
    def __init__(
        self,
        resource_type: str = "Resource",
        resource_id: Optional[str] = None,
        response_body: Optional[Any] = None
    ):
        if resource_id:
            message = f"{resource_type} with ID '{resource_id}' not found."
        else:
            message = f"{resource_type} not found."
        super().__init__(message, status_code=404, response_body=response_body)


class WeeekRateLimitError(WeeekAPIError):
    """
    Rate limit exceeded error (HTTP 429).
    
    Raised when too many requests have been made in a short time period.
    """
    
    def __init__(
        self,
        retry_after: Optional[int] = None,
        response_body: Optional[Any] = None
    ):
        if retry_after:
            message = f"Rate limit exceeded. Please wait {retry_after} seconds before making more requests."
        else:
            message = "Rate limit exceeded. Please wait before making more requests."
        self.retry_after = retry_after
        super().__init__(message, status_code=429, response_body=response_body)


class WeeekValidationError(WeeekAPIError):
    """
    Validation error (HTTP 400).
    
    Raised when the request contains invalid parameters.
    """
    
    def __init__(
        self,
        message: str = "Invalid request parameters.",
        details: Optional[dict] = None,
        response_body: Optional[Any] = None
    ):
        self.details = details
        if details:
            message = f"{message} Details: {details}"
        super().__init__(message, status_code=400, response_body=response_body)


class WeeekServerError(WeeekAPIError):
    """
    Server error (HTTP 5xx).
    
    Raised when the Weeek API server encounters an internal error.
    """
    
    def __init__(
        self,
        status_code: int = 500,
        message: str = "Weeek API server error. Please try again later.",
        response_body: Optional[Any] = None
    ):
        super().__init__(message, status_code=status_code, response_body=response_body)


class WeeekTimeoutError(WeeekAPIError):
    """
    Request timeout error.
    
    Raised when the API request times out.
    """
    
    def __init__(
        self,
        timeout: Optional[int] = None,
        response_body: Optional[Any] = None
    ):
        if timeout:
            message = f"Request timed out after {timeout} seconds. Weeek API server is not responding."
        else:
            message = "Request timed out. Weeek API server is not responding."
        self.timeout = timeout
        super().__init__(message, status_code=None, response_body=response_body)


class WeeekConnectionError(WeeekAPIError):
    """
    Connection error.
    
    Raised when unable to connect to the Weeek API.
    """
    
    def __init__(
        self,
        message: str = "Unable to connect to Weeek API. Please check your internet connection.",
        response_body: Optional[Any] = None
    ):
        super().__init__(message, status_code=None, response_body=response_body)


def create_error_from_response(status_code: int, response_body: Any = None) -> WeeekAPIError:
    """
    Factory function to create appropriate error based on HTTP status code.
    
    Args:
        status_code: HTTP status code from response
        response_body: Response body for additional context
        
    Returns:
        Appropriate WeeekAPIError subclass instance
    """
    error_message = None
    if isinstance(response_body, dict):
        error_message = response_body.get("message") or response_body.get("error")
    
    if status_code == 400:
        return WeeekValidationError(
            message=error_message or "Invalid request parameters.",
            response_body=response_body
        )
    elif status_code == 401:
        return WeeekAuthError(
            message=error_message or "Invalid or expired Weeek token.",
            response_body=response_body
        )
    elif status_code == 403:
        return WeeekForbiddenError(
            message=error_message or "Access denied.",
            response_body=response_body
        )
    elif status_code == 404:
        return WeeekNotFoundError(
            resource_type="Resource",
            response_body=response_body
        )
    elif status_code == 429:
        retry_after = None
        if isinstance(response_body, dict):
            retry_after = response_body.get("retry_after")
        return WeeekRateLimitError(
            retry_after=retry_after,
            response_body=response_body
        )
    elif 500 <= status_code < 600:
        return WeeekServerError(
            status_code=status_code,
            message=error_message or f"Weeek API server error ({status_code}).",
            response_body=response_body
        )
    else:
        return WeeekAPIError(
            message=error_message or f"Weeek API error ({status_code}).",
            status_code=status_code,
            response_body=response_body
        )

