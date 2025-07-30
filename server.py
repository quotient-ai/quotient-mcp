"""
Quotient MCP Server
"""

from starlette.requests import Request
from starlette.responses import JSONResponse
from fastmcp import FastMCP
from pydantic import BaseModel
import requests

mcp = FastMCP("quotient-mcp-server")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(_request: Request):
    """Health check endpoint for deployment platforms"""
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
    available_tools: list[dict], message_history: list[dict]
) -> EvaluationResult:
    """
    Evaluates tool calling behavior via the Limbic Tool Use API.

    Args:
        available_tools: List of tool definitions with name, description, and input_schema
        message_history: Conversation messages with role, content, and optional tool_calls

    Returns:
        EvaluationResult with score and detailed reasoning
    """
    inference_endpoint_url = "https://quotient-ai--tool-call-evaluator-0-5b-api-v0-fastapi-app.modal.run/api/v1/detections/tool-use"

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


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 8888))
    mcp.run(transport="http", host="0.0.0.0", port=port, stateless_http=True)
