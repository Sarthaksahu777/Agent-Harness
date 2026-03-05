# Dockerfile for Agent Harness
# Multi-stage build for a lean production image

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency files first (better layer caching)
COPY pyproject.toml MANIFEST.in ./
COPY src/ ./src/

# Install dependencies and build wheel
RUN pip install --no-cache-dir build \
    && python -m build --wheel

# Production stage
FROM python:3.11-slim as production

WORKDIR /app

# Create non-root user for security
RUN groupadd -r agentharness && useradd -r -g agentharness agentharness

# Copy built wheel from builder stage
COPY --from=builder /app/dist/*.whl /tmp/

# Install the package
RUN pip install --no-cache-dir /tmp/*.whl \
    && rm -rf /tmp/*.whl

# Copy config files
COPY config/ ./config/

# Set ownership to non-root user
RUN chown -R agentharness:agentharness /app

# Switch to non-root user
USER agentharness

# Expose the proxy port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Default command: start the governance proxy
CMD ["python", "-m", "uvicorn", "governance.proxy_enforcer:app", "--host", "0.0.0.0", "--port", "8080"]
