# Agent Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (curl for health checks)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY main.py .

# Create non-root user
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Environment
ENV PYTHONUNBUFFERED=1
ENV AGENT_TYPE=general
ENV MODEL=qwen2.5:3b
ENV OLLAMA_HOST=http://ollama:11434
ENV REDIS_HOST=redis
ENV MAX_CONCURRENT=4
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import httpx; import asyncio; asyncio.run(httpx.AsyncClient().get('http://localhost:8080/health'))" || exit 1

EXPOSE 8080

CMD ["python", "main.py"]
