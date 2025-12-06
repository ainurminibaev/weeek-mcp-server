"""
Weeek MCP Server - Main entry point.

This module initializes and runs the MCP server that exposes
all Weeek API endpoints as MCP tools using FastMCP.

Supports two transport modes:
- stdio: For local MCP clients (Cursor, Claude Desktop, etc.)
- sse: For network access via HTTP (n8n, remote clients, etc.)
"""

import asyncio
import secrets
from typing import Optional

from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from .config import get_config, Config
from .weeek_client import WeeekClient
from .tools import register_all_tools
from .utils.logger import setup_logging, get_logger


# Global logger
logger = get_logger("server")

# Global client instance
_client: Optional[WeeekClient] = None

# Global config
_config: Optional[Config] = None


def create_mcp_server() -> FastMCP:
    """
    Create and configure the FastMCP server with all tools.
    
    Returns:
        Configured FastMCP server instance
    """
    global _config
    
    # Load configuration
    _config = get_config()
    
    # Setup logging
    setup_logging(
        level=_config.log_level,
        format_type=_config.log_format,
        logger_name="weeek-mcp"
    )
    
    logger.info("Initializing Weeek MCP Server")
    logger.info(f"Transport mode: {_config.transport}")
    
    # Create FastMCP server
    mcp = FastMCP("weeek-mcp")
    
    # Create Weeek API client
    global _client
    _client = WeeekClient(
        token=_config.weeek_token,
        base_url=_config.weeek_base_url,
        timeout=_config.request_timeout,
        retry_attempts=_config.retry_attempts,
        retry_delay=_config.retry_delay,
    )
    
    # Register all tools from tools/ modules
    tool_count = register_all_tools(mcp, _client)
    
    logger.info(f"Registered {tool_count} tools")
    logger.info("Weeek MCP Server initialized successfully")
    
    return mcp


# Create the server instance
mcp = create_mcp_server()


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API key authentication.
    
    Validates requests using either:
    - Authorization: Bearer <api_key>
    - X-API-Key: <api_key>
    """
    
    def __init__(self, app, api_key: str):
        super().__init__(app)
        self.api_key = api_key
    
    async def dispatch(self, request: Request, call_next):
        # Allow health check endpoint without auth
        if request.url.path in ["/health", "/healthz"]:
            return await call_next(request)
        
        # Extract API key from headers
        auth_header = request.headers.get("Authorization", "")
        x_api_key = request.headers.get("X-API-Key", "")
        
        provided_key = None
        
        # Check Authorization header (Bearer token)
        if auth_header.startswith("Bearer "):
            provided_key = auth_header[7:]  # Remove "Bearer " prefix
        # Check X-API-Key header
        elif x_api_key:
            provided_key = x_api_key
        
        # Validate API key using constant-time comparison
        if not provided_key or not secrets.compare_digest(provided_key, self.api_key):
            logger.warning(
                f"Unauthorized access attempt from {request.client.host if request.client else 'unknown'}"
            )
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Invalid or missing API key. Use 'Authorization: Bearer <key>' or 'X-API-Key: <key>' header."
                }
            )
        
        return await call_next(request)


def create_authenticated_sse_app(api_key: str) -> Starlette:
    """
    Create SSE app with API key authentication middleware.
    
    Args:
        api_key: The API key required for authentication
        
    Returns:
        Starlette app with authentication middleware
    """
    # Get the base SSE app from FastMCP
    base_app = mcp.sse_app()
    
    # Wrap with authentication middleware
    app = Starlette(
        routes=base_app.routes,
        middleware=[
            Middleware(APIKeyAuthMiddleware, api_key=api_key)
        ],
        on_startup=base_app.on_startup if hasattr(base_app, 'on_startup') else None,
        on_shutdown=base_app.on_shutdown if hasattr(base_app, 'on_shutdown') else None,
    )
    
    # Add health check endpoint
    @app.route("/health")
    @app.route("/healthz")
    async def health_check(request):
        return JSONResponse({"status": "healthy", "service": "weeek-mcp"})
    
    return app


def run_sse_server():
    """
    Run the MCP server in SSE mode using uvicorn.
    
    This allows network access to the MCP server via HTTP SSE transport.
    Useful for remote clients like n8n, web applications, etc.
    
    Requires MCP_API_KEY to be set for authentication.
    """
    import uvicorn
    
    # Validate API key is set for SSE mode
    if not _config.mcp_api_key:
        logger.error("MCP_API_KEY is required when running in SSE mode!")
        logger.error("Set MCP_API_KEY environment variable to secure your server.")
        raise ValueError(
            "MCP_API_KEY must be set when TRANSPORT=sse. "
            "This protects your server from unauthorized access."
        )
    
    if len(_config.mcp_api_key) < 16:
        logger.warning("MCP_API_KEY is too short! Recommended minimum length is 32 characters.")
    
    logger.info(f"Starting SSE server on {_config.server_host}:{_config.server_port}")
    logger.info(f"SSE endpoint: http://{_config.server_host}:{_config.server_port}/sse")
    logger.info(f"Messages endpoint: http://{_config.server_host}:{_config.server_port}/messages")
    logger.info(f"Health endpoint: http://{_config.server_host}:{_config.server_port}/health")
    logger.info("Authentication: ENABLED (use Authorization: Bearer <key> or X-API-Key: <key>)")
    
    # Create app with authentication
    app = create_authenticated_sse_app(_config.mcp_api_key)
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host=_config.server_host,
        port=_config.server_port,
        log_level=_config.log_level.lower(),
    )


def main():
    """
    Main entry point - run the server.
    
    Automatically selects transport based on TRANSPORT environment variable:
    - stdio (default): For local MCP clients
    - sse: For network access via HTTP
    """
    if _config.transport == "sse":
        run_sse_server()
    else:
        # Default to stdio transport
        mcp.run()


if __name__ == "__main__":
    main()
