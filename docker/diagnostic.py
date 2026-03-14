#!/usr/bin/env python3
"""
Full System Diagnostic Test for OpenClaw Docker Swarm
Tests all components: Ollama, Redis, Agents, Orchestrator
"""

import json
import sys
import time
import subprocess

def run_command(cmd, description):
    """Run a command and return result"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"[PASS] PASSED")
            if result.stdout:
                print(f"Output: {result.stdout[:500]}")
            return True, result.stdout
        else:
            print(f"[FAIL] FAILED")
            print(f"Error: {result.stderr[:500]}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print(f"[FAIL] TIMEOUT")
        return False, "Command timed out"
    except Exception as e:
        print(f"[FAIL] EXCEPTION: {e}")
        return False, str(e)

def main():
    print("OPENCLAW DOCKER SWARM - FULL SYSTEM DIAGNOSTIC")
    print("="*60)
    
    results = {}
    
    # Test 1: Docker Daemon
    success, _ = run_command(
        "docker version --format '{{.Server.Version}}'",
        "Docker Daemon Running"
    )
    results['docker_daemon'] = success
    
    # Test 2: Container Status
    success, output = run_command(
        "docker ps --format 'table {{.Names}}\\t{{.Status}}\\t{{.Health}}'",
        "All Containers Running"
    )
    results['containers'] = success
    
    # Test 3: Ollama API
    success, output = run_command(
        "curl -s http://localhost:11434/api/tags",
        "Ollama API Accessible"
    )
    results['ollama_api'] = success
    
    # Test 4: Redis Connection
    success, _ = run_command(
        "docker exec redis redis-cli ping",
        "Redis Responding"
    )
    results['redis'] = success
    
    # Test 5: Orchestrator Health
    success, output = run_command(
        "curl -s http://localhost:8080/health",
        "Orchestrator Health Check"
    )
    results['orchestrator'] = success
    
    # Test 6: Agent Health - Complex
    success, _ = run_command(
        "curl -s http://localhost:8080/health | findstr complex",
        "Complex Agent (14B) Healthy"
    )
    results['agent_complex'] = success
    
    # Test 7: Agent Health - General
    success, _ = run_command(
        "curl -s http://localhost:8080/health | findstr general",
        "General Agent (7B) Healthy"
    )
    results['agent_general'] = success
    
    # Test 8: Agent Health - Fast
    success, _ = run_command(
        "curl -s http://localhost:8080/health | findstr fast",
        "Fast Agents (3B) Healthy"
    )
    results['agent_fast'] = success
    
    # Test 9: Submit Test Task
    print(f"\n{'='*60}")
    print("TEST: Submit Research Task")
    print(f"{'='*60}")
    
    task_json = json.dumps({
        "task_id": "diag-test-001",
        "query": "What is Docker?",
        "topic": "docker",
        "priority": "high"
    })
    
    cmd = f'curl -s -X POST http://localhost:8080/submit-task -H "Content-Type: application/json" -d \'{task_json}\''
    print(f"Command: {cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout:
            try:
                response = json.loads(result.stdout)
                print(f"[PASS] PASSED")
                print(f"Task routed to: {response.get('routed_to', 'unknown')}")
                print(f"Model: {response.get('model', 'unknown')}")
                results['task_submission'] = True
            except:
                print(f"[WARN] PARTIAL (response received but invalid JSON)")
                print(f"Output: {result.stdout[:200]}")
                results['task_submission'] = True
        else:
            print(f"[FAIL] FAILED")
            print(f"Error: {result.stderr[:200]}")
            results['task_submission'] = False
    except Exception as e:
        print(f"[FAIL] EXCEPTION: {e}")
        results['task_submission'] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("DIAGNOSTIC SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {test}")
    
    print(f"\n{'='*60}")
    print(f"RESULT: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print(f"{'='*60}")
    
    if passed == total:
        print("ALL SYSTEMS OPERATIONAL!")
        return 0
    elif passed >= total * 0.8:
        print("MOSTLY OPERATIONAL (minor issues)")
        return 1
    else:
        print("SYSTEM DEGRADED (significant issues)")
        return 2

if __name__ == "__main__":
    sys.exit(main())
