"""
Configuration module for Weeek MCP Server.

Handles all configuration via environment variables with validation.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Literal


class Config(BaseSettings):
    """
    Application configuration loaded from environment variables.
    
    All settings can be overridden via .env file or environment variables.
    Variable names are case-insensitive.
    """
    
    # Weeek API Configuration
    weeek_token: str = Field(
        ...,
        description="Weeek API Bearer token for authentication"
    )
    weeek_base_url: str = Field(
        default="https://api.weeek.net/public/v1",
        description="Base URL for Weeek API"
    )
    
    # HTTP Client Configuration
    request_timeout: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Request timeout in seconds"
    )
    retry_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of retry attempts for failed requests"
    )
    retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Delay between retry attempts in seconds"
    )
    
    # Server Configuration (SSE mode)
    transport: Literal["stdio", "sse"] = Field(
        default="stdio",
        description="Transport mode: 'stdio' for local, 'sse' for network access"
    )
    server_host: str = Field(
        default="0.0.0.0",
        description="Host to bind SSE server (0.0.0.0 for all interfaces)"
    )
    server_port: int = Field(
        default=3847,
        ge=1024,
        le=65535,
        description="Port for SSE server (default: 3847 - non-standard to avoid conflicts)"
    )
    
    # Authentication (for SSE mode)
    mcp_api_key: str = Field(
        default="",
        description="API key for SSE authentication. Required when TRANSPORT=sse"
    )
    
    @field_validator("mcp_api_key")
    @classmethod
    def validate_api_key(cls, v: str, info) -> str:
        """Validate API key is set when using SSE transport."""
        # Validation will be done at runtime when transport is known
        return v
    
    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    log_format: Literal["json", "plain"] = Field(
        default="json",
        description="Log output format"
    )
    
    @field_validator("weeek_token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate that token is not empty or placeholder."""
        if not v or v == "your-api-token-here-1234567890":
            raise ValueError(
                "WEEEK_TOKEN must be set to a valid API token. "
                "Get your token from Weeek Settings → API"
            )
        return v
    
    @field_validator("weeek_base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Ensure base URL doesn't have trailing slash."""
        return v.rstrip("/")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


def get_config() -> Config:
    """
    Get application configuration.
    
    Returns:
        Config: Validated configuration object
        
    Raises:
        ValidationError: If required settings are missing or invalid
    """
    return Config()

