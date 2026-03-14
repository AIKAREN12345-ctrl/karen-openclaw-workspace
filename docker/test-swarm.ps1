# Quick Test Script for OpenClaw Swarm

Write-Host "🧪 Testing OpenClaw Docker Swarm..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Check if services are running
Write-Host "1️⃣ Checking service status..." -ForegroundColor Yellow
docker-compose ps
Write-Host ""

# Test 2: Health check orchestrator
Write-Host "2️⃣ Testing orchestrator health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8080/health" -Method GET -TimeoutSec 10
    Write-Host "✅ Orchestrator: $($response.status)" -ForegroundColor Green
    Write-Host "   Agents: $($response.agents | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Orchestrator not responding: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Health check Ollama
Write-Host "3️⃣ Testing Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 10
    Write-Host "✅ Ollama running with $($response.models.Count) models" -ForegroundColor Green
    foreach ($model in $response.models) {
        Write-Host "   - $($model.name)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Ollama not responding: $_" -ForegroundColor Red
}
Write-Host ""

# Test 4: Submit a test task
Write-Host "4️⃣ Submitting test research task..." -ForegroundColor Yellow
try {
    $body = @{
        task_id = "test-$(Get-Random)"
        query = "What are the benefits of Docker for AI agents?"
        topic = "docker"
        priority = "medium"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8080/submit-task" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
    Write-Host "✅ Task submitted!" -ForegroundColor Green
    Write-Host "   Task ID: $($response.task_id)" -ForegroundColor Gray
    Write-Host "   Routed to: $($response.routed_to) agent" -ForegroundColor Gray
    Write-Host "   Model: $($response.model)" -ForegroundColor Gray
    Write-Host "   Estimated: $($response.estimated_duration)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Task submission failed: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "🎉 Test complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next steps:"
Write-Host "   - Check logs: docker-compose logs -f"
Write-Host "   - Stop swarm: docker-compose down"
Write-Host "   - View results: curl http://localhost:8080/result/TASK_ID"
