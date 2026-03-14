# Orchestrator Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY main.py .

# Create non-root user
RUN useradd -m -u 1000 orchestrator && chown -R orchestrator:orchestrator /app
USER orchestrator

# Environment
ENV PYTHONUNBUFFERED=1
ENV REDIS_HOST=redis
ENV AGENT_COMPLEX_URL=http://agent-complex:8080
ENV AGENT_GENERAL_URL=http://agent-general:8080
ENV AGENT_FAST_URL=http://agent-fast:8080
ENV MAX_AGENTS=10
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import httpx; import asyncio; asyncio.run(httpx.AsyncClient().get('http://localhost:8080/health'))" || exit 1

EXPOSE 8080

CMD ["python", "main.py"]
