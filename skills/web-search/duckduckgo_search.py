#!/usr/bin/env python3
"""
DuckDuckGo Web Search
Free, no API key required
"""

import urllib.request
import urllib.parse
import re
import html

def duckduckgo_search(query, max_results=5):
    """
    Search DuckDuckGo and return results
    """
    # Encode query
    encoded_query = urllib.parse.quote_plus(query)
    
    # DuckDuckGo HTML interface URL
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    # Headers to look like a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html_content = response.read().decode('utf-8')
        
        # Parse results
        results = []
        
        # Find result blocks
        result_pattern = r'<div class="result__body">.*?<a class="result__a" href="([^"]+)">([^<]+)</a>.*?<a class="result__snippet">(.*?)</a>.*?</div>'
        matches = re.findall(result_pattern, html_content, re.DOTALL)
        
        for i, (link, title, snippet) in enumerate(matches[:max_results], 1):
            # Clean up HTML entities
            title = html.unescape(title)
            snippet = html.unescape(re.sub(r'<[^>]+>', '', snippet))
            
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
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: duckduckgo_search.py <query>")
        print("Example: duckduckgo_search.py 'OpenClaw documentation'")
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    print(f"Searching DuckDuckGo for: '{query}'\n")
    
    results = duckduckgo_search(query)
    
    if results and 'error' in results[0]:
        print(f"Error: {results[0]['error']}")
        sys.exit(1)
    
    if not results:
        print("No results found.")
        sys.exit(0)
    
    for result in results:
        print(f"{result['rank']}. {result['title']}")
        print(f"   {result['link']}")
        print(f"   {result['snippet']}")
        print()

if __name__ == "__main__":
    main()
