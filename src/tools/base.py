"""
Base utilities for MCP tool implementations.

Provides common functionality used across all tool modules.
"""

from typing import Any, Dict, Optional, List, Callable
from functools import wraps

from ..utils.logger import get_logger
from ..utils.errors import WeeekAPIError


logger = get_logger("tools")


def handle_api_errors(func: Callable) -> Callable:
    """
    Decorator to handle API errors and format them for MCP response.
    
    Catches WeeekAPIError and other exceptions, returning a structured
    error response instead of raising.
    
    Args:
        func: Async function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Dict[str, Any]:
        try:
            return await func(*args, **kwargs)
        except WeeekAPIError as e:
            logger.error(f"API error in {func.__name__}: {e.message}")
            return {
                "error": True,
                "error_type": e.__class__.__name__,
                "message": e.message,
                "status_code": e.status_code,
            }
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            return {
                "error": True,
                "error_type": "UnexpectedError",
                "message": str(e),
            }
    return wrapper


def build_query_params(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Build query parameters dictionary, filtering out None values.
    
    Args:
        limit: Pagination limit
        offset: Pagination offset
        **kwargs: Additional parameters
        
    Returns:
        Dictionary with non-None values only
    """
    params = {
        "limit": limit,
        "offset": offset,
        **kwargs
    }
    return {k: v for k, v in params.items() if v is not None}


def format_response(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
    """
    Format API response for consistent MCP output.
    
    Args:
        data: Response data from API
        message: Optional message to include
        
    Returns:
        Formatted response dictionary
    """
    response = {
        "success": True,
        "data": data,
    }
    if message:
        response["message"] = message
    return response


def validate_required_params(params: Dict[str, Any], required: List[str]) -> Optional[str]:
    """
    Validate that required parameters are present.
    
    Args:
        params: Parameters dictionary
        required: List of required parameter names
        
    Returns:
        Error message if validation fails, None otherwise
    """
    missing = [p for p in required if params.get(p) is None]
    if missing:
        return f"Missing required parameters: {', '.join(missing)}"
    return None


class ToolResult:
    """
    Helper class for building tool results.
    """
    
    @staticmethod
    def success(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
        """Create successful result."""
        result = {"success": True, "data": data}
        if message:
            result["message"] = message
        return result
    
    @staticmethod
    def error(message: str, error_type: str = "Error", status_code: Optional[int] = None) -> Dict[str, Any]:
        """Create error result."""
        result = {
            "error": True,
            "error_type": error_type,
            "message": message,
        }
        if status_code:
            result["status_code"] = status_code
        return result

