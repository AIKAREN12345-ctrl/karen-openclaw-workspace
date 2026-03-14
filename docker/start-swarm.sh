#!/bin/bash
# start-swarm.sh - Start the OpenClaw Docker swarm

echo "🐳 Starting OpenClaw Agent Swarm..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p workspace/memory/research
mkdir -p workspace/memory
mkdir -p logs

# Pull Ollama models first (this takes time)
echo "📦 Checking Ollama models..."
docker run --rm -v ollama_data:/root/.ollama ollama/ollama:latest sh -c "
    ollama pull qwen2.5:3b 2>/dev/null || echo 'Will pull on first run'
    ollama pull qwen2.5:7b 2>/dev/null || echo 'Will pull on first run'
    ollama pull qwen2.5:14b 2>/dev/null || echo 'Will pull on first run'
" || echo "Models will be pulled on first run"

# Start the swarm
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🔗 Service URLs:"
echo "  Orchestrator: http://localhost:8080"
echo "  Ollama API:   http://localhost:11434"
echo "  Redis:        localhost:6379"

echo ""
echo "🧪 Testing health endpoints..."
sleep 5

curl -s http://localhost:8080/health | jq . || echo "Orchestrator not ready yet"
curl -s http://localhost:11434/api/tags | jq . || echo "Ollama not ready yet"

echo ""
echo "✅ Swarm started!"
echo ""
echo "📋 Useful commands:"
echo "  docker-compose logs -f     # View logs"
echo "  docker-compose ps          # Check status"
echo "  docker-compose down        # Stop swarm"
echo "  docker-compose up -d       # Start swarm"
echo ""
echo "🎯 To test a research task:"
echo "  curl -X POST http://localhost:8080/submit-task \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"task_id\":\"test-1\",\"query\":\"Research Docker best practices\",\"topic\":\"docker\"}'"
echo ""
