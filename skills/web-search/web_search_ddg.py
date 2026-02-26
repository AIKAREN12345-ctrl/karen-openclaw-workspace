#!/usr/bin/env python3
"""
Web Search via DuckDuckGo
Uses web_fetch for reliable extraction
"""

import subprocess
import sys
import re
import html

def search_duckduckgo(query, max_results=5):
    """Search using DuckDuckGo HTML interface via web_fetch"""
    
    # Build URL
    encoded_query = query.replace(' ', '+')
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    try:
        # Use web_fetch via openclaw
        result = subprocess.run(
            ['openclaw', 'web-fetch', url, '--max-chars', '5000'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return [{'error': f'web_fetch failed: {result.stderr}'}]
        
        content = result.stdout
        
        # Parse results from markdown
        results = []
        
        # Find result titles and links
        # Pattern: ## [Title](link)
        pattern = r'##\s*\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)
        
        for i, (title, link) in enumerate(matches[:max_results], 1):
            # Clean up title
            title = html.unescape(title)
            
            # Extract snippet (text after link)
            snippet_match = re.search(
                re.escape(f'[{title}]({link})') + r'\n\n([^\n]+)',
                content
            )
            snippet = snippet_match.group(1) if snippet_match else ''
            snippet = html.unescape(re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', snippet))
            
            results.append({
                'rank': i,
                'title': title,
                'link': link,
                'snippet': snippet[:200] + '...' if len(snippet) > 200 else snippet
            })
        
        return results
        
    except Exception as e:
        return [{'error': str(e)}]

def main():
    if len(sys.argv) < 2:
        print("Usage: web_search.py <query>")
        print("Example: web_search.py 'OpenClaw documentation'")
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    print(f"Searching for: '{query}'\n")
    
    results = search_duckduckgo(query)
    
    if results and 'error' in results[0]:
        print(f"Error: {results[0]['error']}")
        sys.exit(1)
    
    if not results:
        print("No results found.")
        sys.exit(0)
    
    for result in results:
        print(f"{result['rank']}. {result['title']}")
        print(f"   {result['link']}")
        if result['snippet']:
            print(f"   {result['snippet']}")
        print()

if __name__ == "__main__":
    main()
