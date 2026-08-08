#!/usr/bin/env python3
"""Brave Search API wrapper for OpenClaw research subagents."""

import json
import os
import sys
import urllib.request


def get_api_key():
    """Find Brave API key from environment or OpenClaw config."""
    key = os.environ.get("BRAVE_API_KEY")
    if key:
        return key
    # Fallback: read from openclaw.json
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            key = config.get("env", {}).get("BRAVE_API_KEY")
            if key:
                return key
            # Also check models provider
            providers = config.get("models", {}).get("providers", {})
            brave = providers.get("brave", {})
            key = brave.get("apiKey") or brave.get("headers", {}).get("X-Subscription-Token")
            if key:
                return key
        except Exception:
            pass
    return None


def search(query, count=10):
    """Search Brave API and return structured results."""
    api_key = get_api_key()
    if not api_key:
        print(json.dumps({"error": "BRAVE_API_KEY not found"}), file=sys.stderr)
        sys.exit(1)

    url = f"https://api.search.brave.com/res/v1/web/search?q={urllib.request.quote(query)}&count={count}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key,
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        sys.exit(1)

    results = []
    web_results = data.get("web", {}).get("results", [])
    for item in web_results[:count]:
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "description": item.get("description", ""),
        })

    output = {"query": query, "results": results}
    print(json.dumps(output, indent=2))
    # Also save to file for easier retrieval
    out_path = os.path.join(os.path.dirname(__file__), "..", "..", "brave-test-output.json")
    out_path = os.path.abspath(out_path)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: brave_search.py <query>", file=sys.stderr)
        sys.exit(1)
    search(sys.argv[1])
