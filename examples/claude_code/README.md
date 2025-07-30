### `claude-code`
Use the following instructions to use the Quotient MCP server in Claude Code. Once installed Claude Code will evaluate it's own tool calls using Quotient MCP.

1. Install the MCP server in your project:

```bash
claude mcp add --transport http https://mcp.quotientai.co/mcp/
```

2. Copy the CLAUDE.md rule file to your project:

```bash
cp -r examples/claude_code/CLAUDE.md /path/to/your/project/
```