# Weeek MCP Server Dockerfile
# Multi-stage build for minimal image size
# Supports both stdio and SSE transport modes

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY src/ ./src/

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Set Python path
ENV PYTHONPATH=/app

# Environment variables (to be overridden at runtime)
ENV WEEEK_TOKEN=""
ENV WEEEK_BASE_URL="https://api.weeek.net/public/v1"
ENV LOG_LEVEL="INFO"
ENV LOG_FORMAT="json"

# SSE Server Configuration
ENV TRANSPORT="sse"
ENV SERVER_HOST="0.0.0.0"
ENV SERVER_PORT="3847"

# Authentication (REQUIRED for SSE mode - set at runtime!)
ENV MCP_API_KEY=""

# Expose SSE port (non-standard to avoid conflicts)
EXPOSE 3847

# Health check for SSE mode (uses unauthenticated /health endpoint)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3847/health', timeout=5)" || exit 1

# Run the server
CMD ["python", "-m", "src.server"]
