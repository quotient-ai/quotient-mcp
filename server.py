"""
Quotient MCP Server
"""

import argparse
import sys
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastmcp import FastMCP
from pydantic import BaseModel
import requests
from typing import Literal

mcp = FastMCP("quotient-mcp-server")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(_request: Request):
    """Health check endpoint for deployment platforms (HTTP transport only)"""
    return JSONResponse({"status": "ok"})


class EvaluationResult(BaseModel):
    """
    Result of evaluating tool calls.
    """

    score: str
    reason: list[str]


@mcp.tool(
    name="evaluate_tool_call",
    description="""
    Double check Agent Tool Calls with evaluate_tool_call. Evaluate whether an AI agent correctly used available tools in a conversation context.

    Parameters:
    - available_tools: Array of tool definitions

    - message_history: Array of conversation messages
    Example available_tools:
    [
    {
        "name": "google-play-developer",
        "description": "Get apps by a developer on Google Play",
        "input_schema": {
        "type": "object",
        "properties": {
            "devId": {"type": "string", "description": "Developer ID"},
            "num": {"type": "number", "default": 60, "description": "Number of results"},
            "lang": {"type": "string", "default": "en", "description": "Language code"},
            "country": {"type": "string", "default": "us", "description": "Country code"}
        },
        "required": ["devId"]
        }
    }
    ]

    Example message_history:
    [
    {
        "role": "user", 
        "content": "Get 50 apps by 'Example Developer' for US market in English"
    },
    {
        "role": "assistant", 
        "content": "I'll fetch the apps for you.",
        "tool_calls": [{
        "function": {
            "name": "google-play-developer",
            "arguments": {
            "devId": "com.example.developer",
            "num": 50,
            "lang": "en",
            "country": "us"
            }
        }
        }]
    }
    ]

    Returns:
    {
        "score": "correct|incorrect_tool|incorrect_parameter_names|incorrect_parameter_values",
        "reason": ["Detailed explanation of any issues found"]
    }
    """,
)
def evaluate_tool_call(
    available_tools: list[dict], message_history: list[dict], model_size: Literal["0.5B", "3B", "7B"] = "0.5B"
) -> EvaluationResult:
    """
    Evaluates tool calling behavior via the Limbic Tool Use API.

    Args:
        available_tools: List of tool definitions with name, description, and input_schema
        message_history: Conversation messages with role, content, and optional tool_calls
        model_size: Model size to use for evaluation. Can be "0.5B", "3B", or "7B" (default: "0.5B")
    Returns:
        EvaluationResult with score and detailed reasoning
    """

    if model_size == "0.5B":
        inference_endpoint_url = "https://quotient-ai--tool-call-evaluator-0-5b-api-v0-fastapi-app.modal.run/api/v1/detections/tool-use"
    elif model_size == "3B":
        inference_endpoint_url = "https://quotient-ai--tool-call-evaluator-3b-api-v0-fastapi-app.modal.run/api/v1/detections/tool-use"
    elif model_size == "7B":
        inference_endpoint_url = "https://quotient-ai--tool-call-evaluator-7b-api-v0-fastapi-app.modal.run/api/v1/detections/tool-use"
    else:
        raise ValueError(f"Invalid model size: {model_size}. Must be one of: 0.5B, 3B, 7B")

    payload = {"messages": message_history, "available_tools": available_tools}

    try:
        # Make request to Modal endpoint
        response = requests.post(inference_endpoint_url, json=payload, timeout=120)

        if response.status_code == 200:
            result = response.json()
            return EvaluationResult(
                score=result["score"], reason=result.get("reasoning", [])
            )
        else:
            raise RuntimeError(f"API request failed with status {response.status_code}")
    except Exception as e:
        raise e  # re-raise the original exception and let fastmcp handle it


def main():
    """Main entry point with argument parsing for transport selection"""
    parser = argparse.ArgumentParser(description="Quotient MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="http",
        help="Transport method: stdio for local MCP clients, http for remote access"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port for HTTP transport (defaults to PORT env var or 8888)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for HTTP transport (default: 0.0.0.0)"
    )
    
    args = parser.parse_args()
    
    if args.transport == "stdio":
        # Run with stdio transport for local MCP clients
        mcp.run(transport="stdio")
    else:
        # Run with HTTP transport for remote access
        import os
        port = args.port or int(os.environ.get("PORT", 8888))
        mcp.run(
            transport="http", 
            host=args.host, 
            port=port, 
            stateless_http=True
        )


if __name__ == "__main__":
    main()
