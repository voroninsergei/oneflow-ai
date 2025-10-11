# ============================================================================
# Multi-stage Dockerfile for OneFlow.AI
# Optimized for production deployment with security and performance best practices
# ============================================================================

# ============================================================================
# Stage 1: Builder
# ============================================================================
FROM python:3.14-slim as builder

WORKDIR /build

# Install build dependencies in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy only requirements first for optimal layer caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    find /opt/venv -type d -name '__pycache__' -exec rm -rf {} + && \
    find /opt/venv -type f -name '*.pyc' -delete && \
    find /opt/venv -type f -name '*.pyo' -delete

# ============================================================================
# Stage 2: Runtime
# ============================================================================
FROM python:3.14-slim

# Metadata labels (OCI standard)
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

# Environment variables - optimized for production
ENV VERSION=${VERSION} \
    BUILD_DATE=${BUILD_DATE} \
    VCS_REF=${VCS_REF} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies only (minimal footprint)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    ca-certificates \
    tini \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user with specific UID/GID for security
RUN groupadd -g 1000 oneflow && \
    useradd -r -u 1000 -g oneflow -m -s /bin/bash -d /app oneflow && \
    mkdir -p /app/logs /app/data && \
    chown -R oneflow:oneflow /app

# Copy virtual environment from builder (optimized with --chown)
COPY --from=builder --chown=oneflow:oneflow /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code in optimal order (least to most frequently changed)
COPY --chown=oneflow:oneflow README.md .
COPY --chown=oneflow:oneflow setup.py .
COPY --chown=oneflow:oneflow web_server.py .
COPY --chown=oneflow:oneflow src/ ./src/

# Switch to non-root user
USER oneflow

# Expose port
EXPOSE 8000

# Health check with proper intervals
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use tini as init system to handle signals properly
ENTRYPOINT ["/usr/bin/tini", "--"]

# Default command with production-ready settings
CMD ["uvicorn", "web_server:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--log-level", "info", \
     "--no-access-log", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*"]

# ============================================================================
# Build & Run Instructions:
# 
# Build with build arguments:
#   docker build \
#     --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
#     --build-arg VCS_REF=$(git rev-parse --short HEAD) \
#     -t oneflow-ai:latest \
#     -t oneflow-ai:2.0.0 .
#
# Run with environment variables:
#   docker run -d \
#     --name oneflow-ai \
#     -p 8000:8000 \
#     -e DATABASE_URL=postgresql://user:pass@host/db \
#     -e LOG_LEVEL=info \
#     --restart unless-stopped \
#     --memory="2g" \
#     --cpus="2" \
#     --read-only \
#     --tmpfs /tmp \
#     --tmpfs /app/logs \
#     --security-opt no-new-privileges:true \
#     oneflow-ai:latest
#
# Run with docker-compose:
#   docker-compose up -d
#
# Pull from GitHub Container Registry:
#   docker pull ghcr.io/voroninsergei/oneflow-ai:latest
#
# Build for multiple platforms:
#   docker buildx build --platform linux/amd64,linux/arm64 \
#     -t ghcr.io/voroninsergei/oneflow-ai:latest --push .
#
# Scan for vulnerabilities:
#   docker scout cve oneflow-ai:latest
#   trivy image oneflow-ai:latest
# ============================================================================
