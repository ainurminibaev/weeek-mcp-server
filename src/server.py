"""
Weeek MCP Server - Main entry point.

This module initializes and runs the MCP server that exposes
all Weeek API endpoints as MCP tools using FastMCP.

Supports three transport modes:
- stdio: For local MCP clients (Cursor, Claude Desktop, etc.)
- sse: For network access via HTTP SSE (legacy)
- streamable-http: For network access via Streamable HTTP (recommended)
"""

import asyncio
import secrets
from typing import Optional

import json

from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from urllib.parse import parse_qs
from starlette.middleware import Middleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import JSONResponse

from .config import get_config, Config
from .weeek_client import WeeekClient, weeek_token_var
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


class HostRewriteMiddleware:
    """
    Middleware to rewrite Host header to localhost.
    
    This is needed because MCP SDK validates Host header for SSE connections
    to prevent DNS rebinding attacks. When accessing via external IP,
    we need to rewrite the Host to pass validation.
    """
    
    def __init__(self, app, allowed_hosts: list[str] | None = None):
        self.app = app
        # Default allowed hosts include common patterns
        self.allowed_hosts = allowed_hosts or ["*"]
    
    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            # Get original headers
            headers = dict(scope.get("headers", []))
            original_host = headers.get(b"host", b"").decode("utf-8")
            
            # Rewrite host header to localhost with port for MCP SDK validation
            new_headers = []
            for key, value in scope.get("headers", []):
                if key == b"host":
                    # Rewrite to localhost:port to pass MCP SDK validation
                    port = scope.get("server", ("", 3847))[1]
                    new_headers.append((b"host", f"localhost:{port}".encode()))
                else:
                    new_headers.append((key, value))
            
            # Create modified scope with new headers
            scope = dict(scope)
            scope["headers"] = new_headers
            
            # Log for debugging (only on first request)
            if original_host and "logged_host_rewrite" not in scope:
                scope["logged_host_rewrite"] = True
        
        await self.app(scope, receive, send)


class WeeekTokenMiddleware:
    """Extract X-Weeek-Token header and store in contextvar for per-request token."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            headers = dict(scope.get("headers", []))
            weeek_token = headers.get(b"x-weeek-token", b"").decode("utf-8")
            # Also check query parameter (for Claude Desktop connector support)
            if not weeek_token:
                qs = parse_qs(scope.get("query_string", b"").decode("utf-8"))
                if "weeek_token" in qs:
                    weeek_token = qs["weeek_token"][0]
            if weeek_token:
                tok = weeek_token_var.set(weeek_token)
                try:
                    await self.app(scope, receive, send)
                finally:
                    weeek_token_var.reset(tok)
                return
        await self.app(scope, receive, send)


class APIKeyAuthMiddleware:
    """
    Pure ASGI middleware for API key authentication.
    
    Compatible with SSE streaming (unlike BaseHTTPMiddleware).
    
    Validates requests using either:
    - Authorization: Bearer <api_key>
    - X-API-Key: <api_key>
    """
    
    def __init__(self, app, api_key: str):
        self.app = app
        self.api_key = api_key
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            # Pass through non-HTTP requests (websockets, lifespan, etc.)
            await self.app(scope, receive, send)
            return
        
        # Get path from scope
        path = scope.get("path", "")
        
        # Allow health check endpoints without auth
        if path in ["/health", "/healthz"]:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization", b"").decode("utf-8")
        x_api_key = headers.get(b"x-api-key", b"").decode("utf-8")
        
        provided_key = None
        
        # Check Authorization header (Bearer token)
        if auth_header.startswith("Bearer "):
            provided_key = auth_header[7:]  # Remove "Bearer " prefix
        # Check X-API-Key header
        elif x_api_key:
            provided_key = x_api_key
        
        # Check query parameter (for Claude Desktop connector support)
        if not provided_key:
            qs = parse_qs(scope.get("query_string", b"").decode("utf-8"))
            if "api_key" in qs:
                provided_key = qs["api_key"][0]
        
        # Validate API key using constant-time comparison
        if not provided_key or not secrets.compare_digest(provided_key, self.api_key):
            # Get client IP for logging
            client = scope.get("client")
            client_host = client[0] if client else "unknown"
            logger.warning(f"Unauthorized access attempt from {client_host}")
            
            # Send 401 Unauthorized response
            response_body = json.dumps({
                "error": "Unauthorized",
                "message": "Invalid or missing API key. Use 'Authorization: Bearer <key>' or 'X-API-Key: <key>' header."
            }).encode("utf-8")
            
            await send({
                "type": "http.response.start",
                "status": 401,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(response_body)).encode()),
                ],
            })
            await send({
                "type": "http.response.body",
                "body": response_body,
            })
            return
        
        # Auth passed, continue to app
        await self.app(scope, receive, send)


def create_authenticated_sse_app(api_key: str) -> Starlette:
    """
    Create SSE app with API key authentication and host rewrite middleware.
    
    Args:
        api_key: The API key required for authentication
        
    Returns:
        Starlette app with authentication middleware
    """
    # Get the base SSE app from FastMCP
    base_app = mcp.sse_app()
    
    from starlette.routing import Route

    async def health_check(request):
        return JSONResponse({"status": "healthy", "service": "weeek-mcp"})

    routes = list(base_app.routes) + [
        Route("/health", health_check),
        Route("/healthz", health_check),
    ]

    app = Starlette(
        routes=routes,
        middleware=[
            Middleware(TrustedHostMiddleware, allowed_hosts=["*"]),
            Middleware(HostRewriteMiddleware),
            Middleware(APIKeyAuthMiddleware, api_key=api_key),
            Middleware(WeeekTokenMiddleware),
        ],
    )

    return app


def create_authenticated_streamable_app(api_key: str) -> Starlette:
    """
    Create Streamable HTTP app with API key authentication.

    Streamable HTTP is more reliable than SSE — each tool call is
    a single HTTP request/response, no persistent connection needed.
    Must preserve base_app's lifespan for task group initialization.
    """
    base_app = mcp.streamable_http_app()

    from starlette.routing import Route

    async def health_check(request):
        return JSONResponse({"status": "healthy", "service": "weeek-mcp"})

    routes = list(base_app.routes) + [
        Route("/health", health_check),
        Route("/healthz", health_check),
    ]

    # Preserve base_app's lifespan — required for MCP session manager initialization
    app = Starlette(
        routes=routes,
        lifespan=base_app.router.lifespan_context,
        middleware=[
            Middleware(TrustedHostMiddleware, allowed_hosts=["*"]),
            Middleware(HostRewriteMiddleware),
            Middleware(APIKeyAuthMiddleware, api_key=api_key),
            Middleware(WeeekTokenMiddleware),
        ],
    )

    return app


def run_http_server():
    """
    Run the MCP server in network mode using uvicorn.

    Supports both SSE and Streamable HTTP transports.
    Streamable HTTP is preferred — more reliable, no persistent connections.

    Requires MCP_API_KEY to be set for authentication.
    """
    import uvicorn

    if not _config.mcp_api_key:
        logger.error("MCP_API_KEY is required for network transport!")
        raise ValueError("MCP_API_KEY must be set for network transport.")

    if len(_config.mcp_api_key) < 16:
        logger.warning("MCP_API_KEY is too short! Recommended minimum length is 32 characters.")

    transport = _config.transport

    if transport == "streamable-http":
        logger.info(f"Starting Streamable HTTP server on {_config.server_host}:{_config.server_port}")
        logger.info(f"MCP endpoint: http://{_config.server_host}:{_config.server_port}/mcp")
        app = create_authenticated_streamable_app(_config.mcp_api_key)
    else:
        logger.info(f"Starting SSE server on {_config.server_host}:{_config.server_port}")
        logger.info(f"SSE endpoint: http://{_config.server_host}:{_config.server_port}/sse")
        app = create_authenticated_sse_app(_config.mcp_api_key)

    logger.info(f"Health endpoint: http://{_config.server_host}:{_config.server_port}/health")
    logger.info("Authentication: ENABLED")

    uvicorn.run(
        app,
        host=_config.server_host,
        port=_config.server_port,
        log_level=_config.log_level.lower(),
        forwarded_allow_ips="*",
        proxy_headers=True,
    )


def main():
    """
    Main entry point - run the server.
    
    Automatically selects transport based on TRANSPORT environment variable:
    - stdio (default): For local MCP clients
    - sse: For network access via HTTP
    """
    if _config.transport in ("sse", "streamable-http"):
        run_http_server()
    else:
        # Default to stdio transport
        mcp.run()


if __name__ == "__main__":
    main()
