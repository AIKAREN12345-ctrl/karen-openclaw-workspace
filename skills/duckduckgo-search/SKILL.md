---
name: duckduckgo_search
description: Search the web using DuckDuckGo for research tasks
metadata:
  openclaw:
    requires:
      tools: ["web_fetch"]
    tags: ["search", "web", "research", "duckduckgo"]
    author: "Karen"
    version: "1.0.0"
---

# DuckDuckGo Search Skill

Search the web using DuckDuckGo's HTML interface for research tasks.

## Usage

When you need to search the web for information, use this skill with the `web_fetch` tool:

1. **Format the search URL:**
   ```
   https://duckduckgo.com/html?q={search_query}
   ```
   Replace spaces with `+` and URL-encode special characters.

2. **Fetch the results:**
   Use `web_fetch` with the formatted URL to get search results.

3. **Parse the HTML:**
   Extract relevant links, titles, and snippets from the results.

4. **Fetch specific pages:**
   Use `web_fetch` again on interesting result URLs for detailed content.

## Example Workflow

**Task:** Research "OpenClaw best practices"

1. Format URL: `https://duckduckgo.com/html?q=OpenClaw+best+practices`
2. Fetch with `web_fetch`
3. Extract top 5 result URLs
4. Fetch each result page for detailed content
5. Compile findings into a research document

## Tips

- DuckDuckGo HTML interface returns clean, parseable results
- Use `&kl=en-us` for US English results
- Add `&ia=web` to ensure web results
- Results may include instant answers at the top
- Respect rate limits - don't spam searches

## Output Format

Return research findings as structured markdown with:
- Summary of findings
- Key sources (with URLs)
- Detailed notes from each source
- Citations for verification
