# Local LLM Research Pipeline
# Fully autonomous research using local Ollama models
# No cloud dependencies - all processing local

import requests
import json
import os
from datetime import datetime
import time

class LocalResearcher:
    """Autonomous research using local LLM and web sources"""
    
    def __init__(self, model='qwen2.5:14b'):
        self.model = model
        self.ollama_url = 'http://localhost:11434/api/generate'
        self.research_dir = 'C:\\Users\\Karen\\.openclaw\\workspace\\memory\\research'
        os.makedirs(self.research_dir, exist_ok=True)
        
    def query_ollama(self, prompt, temperature=0.7, max_tokens=2000):
        """Query local Ollama model"""
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': temperature,
                        'num_predict': max_tokens
                    }
                },
                timeout=300  # 5 minutes for complex generation
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                return f"[ERROR] Ollama returned {response.status_code}"
                
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def generate_research_topics(self):
        """Generate research topics using local LLM"""
        prompt = """Generate 5 research topics for a small business automation and AI newsletter.
        Focus on practical, actionable insights. Return as a numbered list."""
        
        response = self.query_ollama(prompt, temperature=0.8)
        return response
    
    def summarize_content(self, content, max_length=500):
        """Summarize web content using local LLM"""
        prompt = f"""Summarize the following content in {max_length} characters or less.
        Focus on key insights and actionable takeaways:
        
        {content[:3000]}  # Limit input size
        
        Summary:"""
        
        return self.query_ollama(prompt, temperature=0.3, max_tokens=800)
    
    def analyze_trends(self, research_data):
        """Analyze research data for trends using local LLM"""
        prompt = f"""Analyze the following research data and identify:
        1. Key trends
        2. Actionable insights
        3. Opportunities for small businesses
        
        Data: {research_data[:2000]}
        
        Analysis:"""
        
        return self.query_ollama(prompt, temperature=0.5, max_tokens=1500)
    
    def save_research(self, topic, content, analysis):
        """Save research to file"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{self.research_dir}\\{timestamp}_{topic.replace(' ', '_')[:30]}.md"
        
        report = f"""# Research: {topic}
**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Model:** {self.model} (Local)

## Summary
{content}

## Analysis
{analysis}

---
*Generated locally using Ollama - No cloud dependencies*
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return filename
    
    def run_research_cycle(self):
        """Full autonomous research cycle"""
        print(f"[{datetime.now().strftime('%H:%M')}] Starting local research cycle...")
        
        # Step 1: Generate topics
        topics = self.generate_research_topics()
        print(f"[INFO] Generated topics:\n{topics[:500]}...")
        
        # Step 2: Pick first topic (in real implementation, rotate)
        topic_line = topics.split('\n')[0] if '\n' in topics else topics
        topic = topic_line.strip('1234567890. ')
        
        # Step 3: In real implementation, web search would happen here
        # For now, generate insights directly
        content = self.query_ollama(
            f"Provide a detailed overview of {topic} for small business owners.",
            temperature=0.6,
            max_tokens=2000
        )
        
        # Step 4: Analyze
        analysis = self.analyze_trends(content)
        
        # Step 5: Save
        filename = self.save_research(topic, content, analysis)
        
        print(f"[OK] Research saved to: {filename}")
        return filename

def main():
    """Main entry point - called by cron job"""
    researcher = LocalResearcher()
    
    # Keep model loaded during research (5 min window)
    # Ollama auto-unloads after 5 min of inactivity
    
    try:
        result = researcher.run_research_cycle()
        print(f"[OK] Research cycle complete: {result}")
        return 0
    except Exception as e:
        print(f"[ERROR] Research cycle failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
