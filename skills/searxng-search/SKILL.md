# SearXNG Search

Search the web using SearXNG — a privacy-focused metasearch engine that aggregates results from multiple sources (Brave, Google, Bing, etc.) without requiring an API key.

## When to Use

Use this skill when:
- The user asks for web research on any topic
- DuckDuckGo returns CAPTCHA or empty results
- You need current information, trends, or sources for a research task

## How to Use

### Basic Search

Use `web_fetch` with this URL format:

```
https://search.sapti.me/search?q={encoded_query}
```

Replace spaces with `+` or URL-encode the query.

Example:
```
https://search.sapti.me/search?q=ai+agent+best+practices+2026
```

### Parsing Results

The HTML response contains search results in `<article>` tags with this structure:

```html
<article class="result result-default">
  <h3><a href="URL">Title</a></h3>
  <p>Description snippet...</p>
  <div class="url">domain.com</div>
</article>
```

Extract:
- **URL** from the `<a href="...">` inside `<h3>`
- **Title** from the `<a>` text
- **Description** from the `<p>` text

### Research Workflow

1. **Search once** using SearXNG
2. **Pick 3 results** — do not fetch more pages than necessary
3. **Fetch interesting pages** with `web_fetch` for deeper detail
4. **Synthesize immediately** — 1 concise sentence per finding
5. **Save directly** with `write` — no nested subagents

### Fallback

If SearXNG fails (timeout, empty results, or instance down):
- Use DuckDuckGo: `https://duckduckgo.com/html?q={query}`

## Example

Query: `kdp coloring books trends 2026`

Results will include:
- KDP Easy niche guides
- Medium trend articles
- Reddit discussions
- YouTube tutorials

Pick the 3 most relevant, fetch them, and synthesize.

## Efficiency Rules

- Target completion in under 60 seconds
- If search takes >30s, summarize from search snippets alone
- Always include sources when available

## Notes

- **Instance:** `search.sapti.me` (tested working 2026-04-13)
- **No API key required**
- **Aggregates multiple engines** for broader coverage than DuckDuckGo alone
- **Instance may change** if this one becomes unavailable — check with Ken before switching
