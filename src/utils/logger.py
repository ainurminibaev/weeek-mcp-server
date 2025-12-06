"""
Logging configuration for Weeek MCP Server.

Provides structured JSON logging with sensitive data redaction.
"""

import logging
import sys
import re
from typing import Optional
from pythonjsonlogger import jsonlogger


# Patterns for sensitive data that should be redacted
SENSITIVE_PATTERNS = [
    (re.compile(r'(Bearer\s+)[^\s"\']+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(token["\']?\s*[:=]\s*["\']?)[^"\'\s,}]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(WEEEK_TOKEN\s*=\s*)[^\s]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(Authorization["\']?\s*[:=]\s*["\']?)[^"\'\s,}]+', re.IGNORECASE), r'\1[REDACTED]'),
]


class RedactingFilter(logging.Filter):
    """
    Logging filter that redacts sensitive information from log messages.
    
    Automatically removes API tokens and other sensitive data from logs
    to prevent accidental exposure.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter and redact sensitive data from log record.
        
        Args:
            record: Log record to process
            
        Returns:
            True (always allow the record, but with redacted content)
        """
        if record.msg:
            record.msg = self._redact(str(record.msg))
        
        if record.args:
            record.args = tuple(
                self._redact(str(arg)) if isinstance(arg, str) else arg
                for arg in record.args
            )
        
        return True
    
    def _redact(self, text: str) -> str:
        """Apply all redaction patterns to text."""
        for pattern, replacement in SENSITIVE_PATTERNS:
            text = pattern.sub(replacement, text)
        return text


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter with additional fields and sensitive data redaction.
    """
    
    def add_fields(self, log_record: dict, record: logging.LogRecord, message_dict: dict) -> None:
        """Add custom fields to the log record."""
        super().add_fields(log_record, record, message_dict)
        
        log_record["timestamp"] = self.formatTime(record)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    logger_name: str = "weeek-mcp"
) -> logging.Logger:
    """
    Configure and setup logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Output format ('json' or 'plain')
        logger_name: Name for the logger
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create stream handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Add redacting filter
    handler.addFilter(RedactingFilter())
    
    # Set formatter based on format type
    if format_type.lower() == "json":
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(logger)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Optional name suffix for the logger
        
    Returns:
        Logger instance
    """
    logger_name = "weeek-mcp"
    if name:
        logger_name = f"{logger_name}.{name}"
    
    logger = logging.getLogger(logger_name)
    
    # Ensure the logger has at least a null handler to prevent warnings
    if not logger.handlers and not logger.parent:
        logger.addHandler(logging.NullHandler())
    
    return logger

