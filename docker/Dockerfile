# OpenClaw Agent Dockerfile
# Multi-stage build for efficient image size

# Stage 1: Base with dependencies
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production image
FROM base as production

# Create non-root user
RUN useradd -m -u 1000 agent

# Copy application code
COPY --chown=agent:agent . .

# Switch to non-root user
USER agent

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV AGENT_TYPE=general
ENV MODEL=qwen2.5:3b
ENV OLLAMA_HOST=http://ollama:11434
ENV REDIS_HOST=redis
ENV MAX_CONCURRENT=4

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Start command
CMD ["python", "-m", "agent.main"]
