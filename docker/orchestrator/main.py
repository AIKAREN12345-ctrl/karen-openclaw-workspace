"""
OpenClaw Orchestrator
Routes tasks to appropriate agents based on complexity
"""

import os
import json
import asyncio
import logging
from typing import Optional, List
from datetime import datetime

import httpx
import redis
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
AGENT_COMPLEX_URL = os.getenv('AGENT_COMPLEX_URL', 'http://agent-complex:8080')
AGENT_GENERAL_URL = os.getenv('AGENT_GENERAL_URL', 'http://agent-general:8080')
AGENT_FAST_URL = os.getenv('AGENT_FAST_URL', 'http://agent-fast:8080')
MAX_AGENTS = int(os.getenv('MAX_AGENTS', '10'))

app = FastAPI(title="OpenClaw Orchestrator")

# Redis connection
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

class TaskRequest(BaseModel):
    task_id: str
    query: str
    topic: str
    priority: str = "medium"

class TaskResponse(BaseModel):
    task_id: str
    routed_to: str
    model: str
    status: str
    estimated_duration: str

def analyze_complexity(query: str) -> float:
    """Analyze task complexity (0-1 scale)"""
    complexity = 0.5  # Default medium
    
    # High complexity indicators
    high_indicators = [
        'research', 'analyze', 'compare', 'evaluate',
        'architecture', 'design', 'implement', 'debug',
        'complex', 'difficult', 'challenging'
    ]
    
    # Low complexity indicators
    low_indicators = [
        'simple', 'quick', 'lookup', 'check',
        'list', 'get', 'find', 'search'
    ]
    
    query_lower = query.lower()
    
    for indicator in high_indicators:
        if indicator in query_lower:
            complexity += 0.2
    
    for indicator in low_indicators:
        if indicator in query_lower:
            complexity -= 0.2
    
    # Clamp to 0-1
    return max(0.0, min(1.0, complexity))

def route_task(complexity: float) -> tuple:
    """Route task to appropriate agent"""
    if complexity > 0.7:
        return (AGENT_COMPLEX_URL, "complex", "qwen2.5:14b")
    elif complexity > 0.4:
        return (AGENT_GENERAL_URL, "general", "qwen2.5:7b")
    else:
        return (AGENT_FAST_URL, "fast", "qwen2.5:3b")

@app.get("/health")
async def health_check():
    """Health check"""
    try:
        # Check all agents
        agents = {
            "complex": AGENT_COMPLEX_URL,
            "general": AGENT_GENERAL_URL,
            "fast": AGENT_FAST_URL
        }
        
        agent_status = {}
        async with httpx.AsyncClient() as client:
            for name, url in agents.items():
                try:
                    response = await client.get(f"{url}/health", timeout=5)
                    agent_status[name] = "healthy" if response.status_code == 200 else "unhealthy"
                except:
                    agent_status[name] = "unreachable"
        
        # Check Redis
        redis_ok = redis_client.ping()
        
        all_healthy = all(s == "healthy" for s in agent_status.values()) and redis_ok
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "agents": agent_status,
            "redis": redis_ok
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/submit-task", response_model=TaskResponse)
async def submit_task(task: TaskRequest):
    """Submit task to appropriate agent"""
    try:
        # Analyze complexity
        complexity = analyze_complexity(task.query)
        agent_url, agent_type, model = route_task(complexity)
        
        logger.info(f"Routing task {task.task_id} to {agent_type} agent (complexity: {complexity:.2f})")
        
        # Forward to agent
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{agent_url}/research",
                json={
                    "task_id": task.task_id,
                    "query": task.query,
                    "topic": task.topic,
                    "priority": task.priority
                },
                timeout=300
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
        
        # Estimate duration based on agent type
        duration_estimates = {
            "complex": "60-120s",
            "general": "30-60s",
            "fast": "10-30s"
        }
        
        return TaskResponse(
            task_id=task.task_id,
            routed_to=agent_type,
            model=model,
            status="submitted",
            estimated_duration=duration_estimates[agent_type]
        )
        
    except Exception as e:
        logger.error(f"Task submission failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    """Get task result from Redis"""
    try:
        result = redis_client.get(f"result:{task_id}")
        if result:
            return json.loads(result)
        else:
            raise HTTPException(status_code=404, detail="Result not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    """Get orchestrator status"""
    return {
        "max_agents": MAX_AGENTS,
        "agents": {
            "complex": AGENT_COMPLEX_URL,
            "general": AGENT_GENERAL_URL,
            "fast": AGENT_FAST_URL
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
