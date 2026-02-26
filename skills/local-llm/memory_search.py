#!/usr/bin/env python3
"""
Memory Search Tool
Search through memory files using local embeddings
"""

import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

MEMORY_DIR = Path("C:/Users/Karen/.openclaw/workspace/memory")
EMBEDDINGS_FILE = MEMORY_DIR / "embeddings.json"
MODEL_NAME = 'all-MiniLM-L6-v2'

def load_embeddings():
    """Load the embeddings index"""
    if not EMBEDDINGS_FILE.exists():
        print("No embeddings found. Run setup-memory-search.py first.")
        return None, None
    
    with open(EMBEDDINGS_FILE, 'r') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} memory chunks")
    return data

def search_memories(query, top_k=5):
    """Search memories by semantic similarity"""
    data = load_embeddings()
    if not data:
        return []
    
    print(f"Loading model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME, cache_folder='C:/Users/Karen/Models')
    
    query_emb = model.encode(query)
    
    results = []
    for item in data:
        emb = np.array(item['embedding'])
        sim = np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb))
        results.append((sim, item))
    
    results.sort(key=lambda x: x[0], reverse=True)
    return results[:top_k]

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: memory_search.py <query>")
        print("Example: memory_search.py 'VNC setup'")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    print(f"Searching for: '{query}'\n")
    
    results = search_memories(query)
    
    if not results:
        print("No results found.")
        return
    
    print(f"Top {len(results)} results:\n")
    for i, (score, item) in enumerate(results, 1):
        print(f"{i}. [{item['file']}] (score: {score:.3f})")
        content = item['content'][:150].encode('ascii', 'ignore').decode('ascii')
        print(f"   {content}...")
        print()

if __name__ == "__main__":
    main()
