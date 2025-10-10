# ============================================================================
# Multi-stage Dockerfile for OneFlow.AI
# Optimized for production deployment
# ============================================================================

# ============================================================================
# Stage 1: Builder
# ============================================================================
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 2: Runtime
# ============================================================================
FROM python:3.11-slim

# Metadata labels
LABEL org.opencontainers.image.title="OneFlow.AI" \
      org.opencontainers.image.description="AI Model Aggregator with Pricing, Routing, and Analytics" \
      org.opencontainers.image.vendor="Sergey Voronin" \
      org.opencontainers.image.source="https://github.com/voroninsergei/oneflow-ai" \
      org.opencontainers.image.licenses="Proprietary" \
      org.opencontainers.image.version="2.0.0"

# Build arguments
ARG VERSION=2.0.0
ARG BUILD_DATE
ARG VCS_REF

# Environment variables
ENV VERSION=${VERSION} \
    BUILD_DATE=${BUILD_DATE} \
    VCS_REF=${VCS_REF} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash oneflow && \
    mkdir -p /app /app/logs /app/data && \
    chown -R oneflow:oneflow /app

# Copy virtual environment from builder
COPY --from=builder --chown=oneflow:oneflow /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=oneflow:oneflow src/ ./src/
COPY --chown=oneflow:oneflow web_server.py .
COPY --chown=oneflow:oneflow setup.py .
COPY --chown=oneflow:oneflow README.md .

# Switch to non-root user
USER oneflow

# Add virtual environment to PATH
ENV PATH="/opt/venv/bin:$PATH"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "web_server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ============================================================================
# Usage:
# 
# Build:
#   docker build -t oneflow-ai:latest .
#
# Run:
#   docker run -d -p 8000:8000 \
#     -e DATABASE_URL=postgresql://user:pass@host/db \
#     oneflow-ai:latest
#
# Pull from GHCR:
#   docker pull ghcr.io/voroninsergei/oneflow-ai:latest
# ============================================================================
