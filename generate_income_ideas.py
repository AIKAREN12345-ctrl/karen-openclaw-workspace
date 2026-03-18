import requests
import json

prompt = '''Generate 10 creative passive income ideas for an AI assistant with these capabilities:
- Web research and data gathering
- Content creation and writing
- Code generation and automation
- File processing and organization
- Local LLM (qwen2.5:14b) for inference
- 24/7 operation via cron jobs
- Can create and manage digital products

Focus on ideas that:
1. Require minimal ongoing human intervention
2. Can be automated with scripts
3. Generate recurring revenue
4. Leverage AI content generation
5. Are realistic for a solo operator

For each idea, provide:
- Name
- Setup effort (Low/Medium/High)
- Time to first revenue
- Ongoing maintenance
- Revenue potential ($/month)
- Why it fits AI automation

Format as a numbered list.'''

response = requests.post('http://localhost:11434/api/generate', json={
    'model': 'qwen2.5:14b',
    'prompt': prompt,
    'stream': False,
    'options': {'temperature': 0.8, 'num_predict': 2000}
}, timeout=180)

print(response.json()['response'])
