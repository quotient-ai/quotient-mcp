# Claude Desktop Integration

Complete setup guide for integrating Quotient MCP with Claude Desktop.

## Prerequisites

- Install `uv`: `brew install uv` (macOS) or follow [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)

## Setup Steps

### 1. Clone the Repository

```bash
git clone https://github.com/quotient-ai/quotient-mcp
cd quotient-mcp
```

### 2. Configure Claude Desktop

Add the following configuration to your Claude Desktop config file:

**Access your config file:**
- **via UI**: Settings → Developer → Local MCP → Edit Config
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Add this configuration:**

```json
{
  "mcpServers": {
    "quotient-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--with", "fastmcp>=2.10.6",
        "--with", "mcp==1.12.2", 
        "--with", "requests>=2.28.0",
        "fastmcp",
        "run",
        "/absolute/path/to/your/quotient-mcp/server.py"
      ]
    }
  }
}
```

> **Important:** Replace `/absolute/path/to/your/quotient-mcp/server.py` with the full absolute path to your `server.py` file.

### 3. Configure Personal Preferences (Recommended)

To automatically evaluate tool usage, add this rule to your Claude Desktop preferences:

1. Go to **Settings → Profile → Personal Preferences**
2. Copy and paste the following:

```
After making any tool call always use quotient-mcp evaluate_tool_call to evaluate proper tool use.
```

### 4. Restart Claude Desktop

Completely quit Claude Desktop and reopen it for the changes to take effect.

## Usage

Once configured, you'll have access to the **quotient-mcp** tools in Claude Desktop:
