#!/usr/bin/env python3
"""
Generate embeddings for all memory files
"""

import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

MEMORY_DIR = Path("C:/Users/Karen/.openclaw/workspace/memory")
EMBEDDINGS_FILE = MEMORY_DIR / "embeddings.json"
MODEL_NAME = 'all-MiniLM-L6-v2'

def chunk_content(content, chunk_size=500, overlap=100):
    """Split content into overlapping chunks"""
    chunks = []
    start = 0
    while start < len(content):
        end = min(start + chunk_size, len(content))
        chunks.append(content[start:end])
        start += chunk_size - overlap
    return chunks

def generate_embeddings():
    """Generate embeddings for all memory files"""
    print(f"Loading model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME, cache_folder='C:/Users/Karen/Models')
    
    embeddings_data = []
    
    # Process all markdown files except embeddings.json
    for md_file in sorted(MEMORY_DIR.glob("*.md")):
        print(f"Processing {md_file.name}...")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into chunks
        chunks = chunk_content(content)
        
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding = model.encode(chunk).tolist()
            
            embeddings_data.append({
                "file": md_file.name,
                "chunk": i,
                "content": chunk[:500],  # Store first 500 chars
                "embedding": embedding
            })
    
    # Save embeddings
    with open(EMBEDDINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(embeddings_data, f)
    
    print(f"\nGenerated {len(embeddings_data)} embeddings")
    print(f"Saved to {EMBEDDINGS_FILE}")

if __name__ == "__main__":
    generate_embeddings()
