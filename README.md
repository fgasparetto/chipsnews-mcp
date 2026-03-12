<!-- mcp-name: io.github.fgasparetto/chipsnews-mcp -->

# ChipsNews MCP Server

MCP (Model Context Protocol) server for [ChipsNews](https://news.chipsbuilder.com) — manage news configuration, sources, articles, and fetch triggers from Claude Code, Claude Desktop, or any MCP client.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A ChipsNews API key

## Quick Start

No installation needed with `uv`:

```bash
uv run --script server.py
```

Or install manually:

```bash
pip install "mcp[cli]" httpx
python server.py
```

## Configuration

The server uses environment variables for authentication:

| Variable | Description | Default |
|----------|-------------|---------|
| `CHIPSNEWS_API_URL` | API base URL | `https://news.chipsbuilder.com` |
| `CHIPSNEWS_API_KEY` | Your API key (Bearer token) | — |

### Claude Code

Add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "chipsnews": {
      "command": "uv",
      "args": ["run", "--script", "/path/to/chipsnews-mcp/server.py"],
      "env": {
        "CHIPSNEWS_API_URL": "https://news.chipsbuilder.com",
        "CHIPSNEWS_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "chipsnews": {
      "command": "uv",
      "args": ["run", "--script", "/path/to/chipsnews-mcp/server.py"],
      "env": {
        "CHIPSNEWS_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Available Tools

### Configuration

| Tool | Description |
|------|-------------|
| `get_config` | Get news configuration (keywords, language, frequency, etc.) |
| `update_config` | Update configuration fields (keywords, language, frequency, auto_publish, notification_email, pin_duration_hours, etc.) |

### Sources

| Tool | Description |
|------|-------------|
| `list_sources` | List all news sources |
| `create_source` | Create a new source (rss, google, reddit) |
| `update_source` | Update an existing source |
| `delete_source` | Delete a source |

### Articles

| Tool | Description |
|------|-------------|
| `list_articles` | List articles with optional filters (status, keyword, source, page) |
| `get_article` | Get full details of a single article |
| `approve_article` | Approve and publish an article |
| `reject_article` | Reject an article |
| `pin_article` | Pin an article to the top (TOP) |
| `unpin_article` | Remove pin from an article |
| `lock_article` | Lock an article to protect from rotation cleanup |
| `unlock_article` | Unlock an article |
| `delete_article` | Delete an article |
| `delete_all_articles` | Delete ALL articles (use with caution) |

### Fetch & Stats

| Tool | Description |
|------|-------------|
| `trigger_fetch` | Trigger a manual news fetch from all active sources |
| `get_stats` | Get usage statistics: article counts, API calls, fetch history |

## Usage Examples

Once configured, use natural language in Claude:

- *"List all news sources"*
- *"Add an RSS feed for TechCrunch"*
- *"Show published articles"*
- *"Approve article 42"*
- *"Pin the top article"*
- *"Trigger a news fetch"*
- *"Show news stats"*
- *"Update keywords to AI, startup, fintech"*

## Authentication

The server uses API key authentication (Bearer token). Pass your key via the `CHIPSNEWS_API_KEY` environment variable.

## License

MIT
