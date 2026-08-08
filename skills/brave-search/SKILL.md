# brave-search

Search the web using the Brave Search API. Returns structured web results with titles, URLs, and descriptions.

## Usage

This skill provides a Python script that queries the Brave Search API using the configured `BRAVE_API_KEY`.

### Running a search

```bash
python C:\Users\Karen\.openclaw\workspace\skills\brave-search\brave_search.py "your search query"
```

### Output

Results are printed as JSON to stdout:

```json
{
  "query": "your search query",
  "results": [
    {
      "title": "...",
      "url": "...",
      "description": "..."
    }
  ]
}
```

## Configuration

Requires `BRAVE_API_KEY` in `~/.openclaw/openclaw.json` env or the `brave` models provider section.

## Example

```bash
python C:\Users\Karen\.openclaw\workspace\skills\brave-search\brave_search.py "OpenClaw latest updates 2026"
```
