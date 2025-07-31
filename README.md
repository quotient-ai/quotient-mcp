# Quotient MCP

An MCP server for evaluating tool calls and AI agent interactions. Analyzes and scores tool usage correctness in conversational AI contexts.

## Streamable HTTP Remote MCP Server
The Quotient MCP is available at [https://mcp.quotientai.co/mcp/](https://mcp.quotientai.co/mcp/)

**Note:** The server supports both HTTP transport (for remote hosting) and stdio transport (for local MCP client integration).

## Quick Start

### Docker

```bash
docker compose up quotient-mcp --build
```

The server will be available at `http://localhost:8888` with a health check at `/health`.

### Local Installation

Install the package:
```bash
uv sync
```

#### Option 1: Stdio Transport (for MCP clients)

Run with stdio transport for direct MCP client integration:
```bash
uv run python server.py --transport stdio
```

This mode is designed for integration with MCP clients that manage the server process directly through standard input/output.

#### Option 2: HTTP Transport (for remote hosting)

Run the HTTP server:
```bash
uv run python server.py --transport http --port 8888
```
### Testing

Test the server functionality:
```bash
uv run python test_client.py
```

## Quotient MCP Functions

### `evaluate_tool_call`

Evaluates tool call correctness in conversation contexts.

**Input:**
- `available_tools`: List of tools with schemas
- `message_history`: Conversation history

**Output:**
- `score`: `"correct"`, `"incorrect_tool"`, `"incorrect_parameter_names"`, or `"incorrect_parameter_values"`
- `reason`: Detailed explanation

## Underlying Model

This MCP server is powered by [**limbic-tool-use-0.5B-32K**](https://huggingface.co/quotientai/limbic-tool-use-0.5B-32K), a specialized language model fine-tuned for evaluating tool usage in AI agent interactions.

### Example Usage

**Input:**
```json
{
  "available_tools": [
    {
      "name": "get_weather",
      "description": "Get current weather for a location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "City name"
          },
          "units": {
            "type": "string",
            "enum": ["celsius", "fahrenheit"],
            "description": "Temperature units"
          }
        },
        "required": ["location"]
      }
    }
  ],
  "message_history": [
    {
      "role": "user",
      "content": "What's the weather like in New York?"
    },
    {
      "role": "assistant",
      "content": "I'll check the weather in New York for you.",
      "tool_calls": [
        {
          "id": "call_123",
          "type": "function",
          "function": {
            "name": "get_weather",
            "arguments": "{\"location\": \"New York\", \"units\": \"fahrenheit\"}"
          }
        }
      ]
    }
  ]
}
```

**Output:**
```json
{
  "score": "correct",
  "reason": "The tool call is appropriate for the user's request. The 'get_weather' function is correctly selected, the required 'location' parameter is properly set to 'New York', and the optional 'units' parameter is reasonably set to 'fahrenheit'. The function arguments are properly formatted as JSON."
}
```

**Example of Incorrect Usage:**

**Input:**
```json
{
  "available_tools": [
    {
      "name": "send_email",
      "description": "Send an email",
      "parameters": {
        "type": "object",
        "properties": {
          "recipient": {"type": "string"},
          "subject": {"type": "string"},
          "body": {"type": "string"}
        },
        "required": ["recipient", "subject", "body"]
      }
    }
  ],
  "message_history": [
    {
      "role": "user",
      "content": "What's the weather like in Paris?"
    },
    {
      "role": "assistant",
      "content": "I'll send an email about that.",
      "tool_calls": [
        {
          "id": "call_456",
          "type": "function",
          "function": {
            "name": "send_email",
            "arguments": "{\"recipient\": \"user@example.com\", \"subject\": \"Weather\", \"body\": \"Weather info\"}"
          }
        }
      ]
    }
  ]
}
```

**Output:**
```json
{
  "score": "incorrect_tool",
  "reason": "The selected tool 'send_email' is inappropriate for the user's request about weather information. The user asked for current weather in Paris, but the assistant chose to send an email instead of using a weather-related tool or indicating that no weather tool is available."
}
```

## Code and Configuration Examples

This repository contains a collection of agent configurations and code examples for integrating with the Quotient MCP server:

### Integration Examples

- **[OpenAI Agent SDK](examples/openai_agent_sdk/)** - Complete integration example with the OpenAI Agents SDK, including multi-agent setup with MCP server connectivity
- **[Cursor IDE](examples/.cursor/)** - Configuration files and rules for Cursor IDE integration
- **[Claude Code](examples/claude_code/)** - Configuration files for Claude Code integration
- **[Claude Desktop](examples/claude_desktop/)** - Complete setup guide for Claude Desktop integration with stdio transport

We will continue to add new integrations as they become available.