import asyncio
from fastmcp import Client

client = Client("http://127.0.0.1:8888/mcp/")

available_tools = [
    {
        "name": "search_web",
        "description": "Search the web for information",
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Search query"}},
            "required": ["query"],
        },
    }
]

message_history = [
    {"role": "user", "content": "Can you search for Python tutorials?"},
    {
        "role": "assistant",
        "content": "I'll search for Python tutorials for you.",
        "tool_calls": [
            {
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": "search_web",
                    "arguments": '{"query": "Python tutorials"}',
                },
            }
        ],
    },
]


async def test_evaluate_tool_call():
    async with client:
        result = await client.call_tool(
            "evaluate_tool_call",
            {"available_tools": available_tools, "message_history": message_history},
        )
        print("Evaluation Result: ", result)
        print(f"Score: {result.data.score}")
        print(f"Reason: {result.data.reason}")


asyncio.run(test_evaluate_tool_call())
