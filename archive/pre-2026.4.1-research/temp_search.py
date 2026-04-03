#!/usr/bin/env python3
import urllib.request
import urllib.parse
import re
import html

query = 'AI news March 2025 latest developments'
encoded = urllib.parse.quote_plus(query)
url = f'https://html.duckduckgo.com/html/?q={encoded}'

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    with urllib.request.urlopen(req, timeout=30) as response:
        content = response.read().decode('utf-8')
    
    # Find result titles and links
    pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
    matches = re.findall(pattern, content)
    
    print(f'Found {len(matches)} results:\n')
    for i, (link, title) in enumerate(matches[:5], 1):
        title = re.sub(r'<[^>]+>', '', title)
        title = html.unescape(title)
        print(f'{i}. {title}')
        print(f'   {link}\n')
        
except Exception as e:
    print(f'Error: {e}')
