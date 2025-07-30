# Example Configurations

This directory contains configuration files that can be copied into MCP client projects to integrate with this MCP server.

## Available Configurations

### `.cursor` Directory

The `.cursor` directory contains configuration files for Cursor IDE integration:

#### Files Included:

- **`mcp.json`** - Configuration file that makes the MCP server available to the coding agent
- **`rules/evaluate-tool-call.mdc`** - Ruleset that instructs the coding agent to use the `evaluate_tool_call` function after making tool calls

#### Usage:

1. Copy the entire `.cursor` directory into your Cursor project root
2. The MCP server will be automatically available to the coding agent
3. The evaluation rules will be applied to enhance tool call reliability

## Installation

Simply copy the desired configuration directory to your target project:

```bash
cp -r example_configs/.cursor /path/to/your/project/
```

### `claude-code`

1. Install the MCP server in your project:

```bash
claude mcp add --transport http https://mcp.quotientai.co/mcp/
```

2. Copy configuration files to your project:

```bash
cp -r example_configs/.claude /path/to/your/project/
```