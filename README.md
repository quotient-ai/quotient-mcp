# Quotient MCP

An MCP server for evaluating tool calls and AI agent interactions. Analyzes and scores tool usage correctness in conversational AI contexts.

## Quick Start

### Docker (Recommended)

```bash
docker compose up quotient-mcp --build
```

The server will be available at `http://localhost:8888` with a health check at `/health`.

### Local Installation

```bash
uv install
```

Run the HTTP server:
```bash
python server.py
```
### Test Script

Run the included test client to test the MCP server.
```bash
python test_client.py
```

## Example Configurations

The `example_configs/` directory contains ready-to-use configurations for different IDEs and tools:

- **`.cursor/`** - Cursor IDE integration with automatic MCP server availability and evaluation rules
- Copy to your project: `cp -r example_configs/.cursor /path/to/your/project/`

## Quotient MCP Functions

### `evaluate_tool_call`

Evaluates tool call correctness in conversation contexts.

**Input:**
- `available_tools`: List of tools with schemas
- `message_history`: Conversation history

**Output:**
- `score`: `"correct"`, `"incorrect_tool"`, `"incorrect_parameter_names"`, or `"incorrect_parameter_values"`
- `reason`: Detailed explanation


## Development

Project uses `fastmcp` for the MCP framework.



