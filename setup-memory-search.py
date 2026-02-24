from sentence_transformers import SentenceTransformer
import json
import numpy as np
from pathlib import Path

print("Loading MiniLM model...")
model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='C:/Users/Karen/Models')
print(f"Model ready: {model.get_sentence_embedding_dimension()} dimensions")

memory_dir = Path("C:/Users/Karen/.openclaw/workspace/memory")
embeddings_data = []

for file_path in sorted(memory_dir.glob("*.md")):
    print(f"Processing {file_path.name}...")
    content = file_path.read_text(encoding='utf-8')
    chunks = [c.strip() for c in content.split('\n\n') if len(c.strip()) > 50]
    
    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()
        embeddings_data.append({
            'file': file_path.name,
            'chunk': i,
            'content': chunk[:300],
            'embedding': embedding
        })

# Save
output_file = memory_dir / "embeddings.json"
with open(output_file, 'w') as f:
    json.dump(embeddings_data, f)

print(f"Indexed {len(embeddings_data)} chunks to {output_file}")

# Test search
query = "business idea"
query_emb = model.encode(query)

results = []
for item in embeddings_data:
    emb = np.array(item['embedding'])
    sim = np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb))
    results.append((sim, item))

results.sort(reverse=True)
print(f"\nTop results for '{query}':")
for sim, item in results[:3]:
    print(f"  [{item['file']}] {item['content'][:80]}... (score: {sim:.3f})")
