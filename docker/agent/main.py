"""
OpenClaw Agent - Docker Container
Handles research tasks with file saving and DuckDuckGo search
"""

import os
import json
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

import httpx
import redis
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
AGENT_TYPE = os.getenv('AGENT_TYPE', 'general')
MODEL = os.getenv('MODEL', 'qwen2.5:3b')
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://ollama:11434')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
MAX_CONCURRENT = int(os.getenv('MAX_CONCURRENT', '4'))
WORKSPACE_DIR = os.getenv('WORKSPACE_DIR', '/app/workspace')

app = FastAPI(title=f"OpenClaw Agent - {AGENT_TYPE}")

# Redis connection
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

class ResearchTask(BaseModel):
    task_id: str
    query: str
    topic: str
    priority: str = "medium"
    
class ResearchResult(BaseModel):
    task_id: str
    agent_type: str
    model: str
    query: str
    result: str
    timestamp: str
    duration_seconds: float
    file_path: Optional[str] = None

def save_research_to_file(topic: str, content: str) -> str:
    """Save research to workspace file"""
    try:
        # Create research directory
        research_dir = Path(WORKSPACE_DIR) / "memory" / "research"
        research_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with date
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"{date_str}_{topic}.md"
        file_path = research_dir / filename
        
        # Write content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Saved research to {file_path}")
        return str(file_path)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        return None

async def duckduckgo_search(query: str) -> str:
    """Search DuckDuckGo for information"""
    try:
        # Use DuckDuckGo HTML interface
        search_url = f"https://duckduckgo.com/html?q={query.replace(' ', '+')}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                search_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                # Extract search results (simplified)
                return response.text[:5000]  # Return first 5000 chars for analysis
            else:
                return f"Search failed: {response.status_code}"
    except Exception as e:
        logger.error(f"DuckDuckGo search failed: {e}")
        return f"Search error: {str(e)}"

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Ollama
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
            ollama_ok = response.status_code == 200
        
        # Check Redis
        redis_ok = redis_client.ping()
        
        return {
            "status": "healthy" if ollama_ok and redis_ok else "degraded",
            "agent_type": AGENT_TYPE,
            "model": MODEL,
            "ollama": ollama_ok,
            "redis": redis_ok
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/research", response_model=ResearchResult)
async def do_research(task: ResearchTask, background_tasks: BackgroundTasks):
    """Execute research task with file saving"""
    start_time = datetime.now()
    
    try:
        logger.info(f"[{AGENT_TYPE}] Starting research: {task.query}")
        
        # Step 1: Search DuckDuckGo
        logger.info(f"[{AGENT_TYPE}] Searching DuckDuckGo...")
        search_results = await duckduckgo_search(task.query)
        
        # Step 2: Analyze with Ollama
        logger.info(f"[{AGENT_TYPE}] Analyzing with {MODEL}...")
        prompt = f"""Research Topic: {task.query}

Search Results:
{search_results[:3000]}

Please provide a comprehensive research summary including:
1. Key findings
2. Important details
3. Sources mentioned
4. Conclusion

Format as markdown."""
        
        analysis = await call_ollama(prompt)
        
        # Step 3: Format full research document
        duration = (datetime.now() - start_time).total_seconds()
        
        full_content = f"""# {task.topic.replace('_', ' ').title()} Research - {datetime.now().strftime('%Y-%m-%d')}

**Date:** {datetime.now().isoformat()}  
**Topic:** {task.topic}  
**Agent:** {AGENT_TYPE} ({MODEL})  
**Query:** {task.query}  
**Duration:** {duration:.2f}s

---

{analysis}

---

*Research conducted by OpenClaw Agent Swarm*
"""
        
        # Step 4: Save to file
        file_path = save_research_to_file(task.topic, full_content)
        
        # Step 5: Create result
        research_result = ResearchResult(
            task_id=task.task_id,
            agent_type=AGENT_TYPE,
            model=MODEL,
            query=task.query,
            result=analysis,
            timestamp=datetime.now().isoformat(),
            duration_seconds=duration,
            file_path=file_path
        )
        
        # Step 6: Store in Redis
        redis_client.setex(
            f"result:{task.task_id}",
            3600,
            json.dumps(research_result.dict())
        )
        
        logger.info(f"[{AGENT_TYPE}] Completed research in {duration:.2f}s, saved to {file_path}")
        
        return research_result
        
    except Exception as e:
        logger.error(f"Research failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def call_ollama(prompt: str) -> str:
    """Call Ollama API"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_ctx": 4096
                }
            },
            timeout=300
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama error: {response.text}")
        
        data = response.json()
        return data.get('response', '')

@app.get("/status")
async def get_status():
    """Get agent status"""
    return {
        "agent_type": AGENT_TYPE,
        "model": MODEL,
        "max_concurrent": MAX_CONCURRENT,
        "ollama_host": OLLAMA_HOST,
        "redis_host": REDIS_HOST,
        "workspace_dir": WORKSPACE_DIR
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
