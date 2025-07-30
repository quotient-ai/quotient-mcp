# The example extends the following example from the OpenAI Agent SDK:
# https://github.com/openai/openai-agents-python/blob/main/examples/customer_service/main.py

from __future__ import annotations as _annotations

import asyncio
import random
import uuid
import sys
import traceback

from pydantic import BaseModel

try:
    from agents import (
        Agent,
        HandoffOutputItem,
        ItemHelpers,
        MessageOutputItem,
        RunContextWrapper,
        Runner,
        ToolCallItem,
        ToolCallOutputItem,
        TResponseInputItem,
        function_tool,
        handoff,
        trace,
    )
    from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
    from agents.mcp import MCPServerStreamableHttp
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    print(
        "💡 Make sure to install the OpenAI Agent SDK: pip install openai-agents>=0.2.3"
    )
    sys.exit(1)

# Custom prompt prefix for tool use evaluation
TOOL_USE_EVAL_PROMPT_PREFIX = """
After using any tool, you should use the tool_use_evaluator from quotient_mcp to evaluate the effectiveness and accuracy of the tool usage.
"""

### CONTEXT


class AirlineAgentContext(BaseModel):
    passenger_name: str | None = None
    confirmation_number: str | None = None
    seat_number: str | None = None
    flight_number: str | None = None


### TOOLS


@function_tool(
    name_override="faq_lookup_tool",
    description_override="Lookup frequently asked questions.",
)
async def faq_lookup_tool(question: str) -> str:
    if "bag" in question or "baggage" in question:
        return (
            "You are allowed to bring one bag on the plane. "
            "It must be under 50 pounds and 22 inches x 14 inches x 9 inches."
        )
    elif "seats" in question or "plane" in question:
        return (
            "There are 120 seats on the plane. "
            "There are 22 business class seats and 98 economy seats. "
            "Exit rows are rows 4 and 16. "
            "Rows 5-8 are Economy Plus, with extra legroom. "
        )
    elif "wifi" in question:
        return "We have free wifi on the plane, join Airline-Wifi"
    return "I'm sorry, I don't know the answer to that question."


@function_tool
async def update_seat(
    context: RunContextWrapper[AirlineAgentContext],
    confirmation_number: str,
    new_seat: str,
) -> str:
    """
    Update the seat for a given confirmation number.

    Args:
        confirmation_number: The confirmation number for the flight.
        new_seat: The new seat to update to.
    """
    # Update the context based on the customer's input
    context.context.confirmation_number = confirmation_number
    context.context.seat_number = new_seat
    # Ensure that the flight number has been set by the incoming handoff
    assert context.context.flight_number is not None, "Flight number is required"
    return f"Updated seat to {new_seat} for confirmation number {confirmation_number}"


### HOOKS


async def on_seat_booking_handoff(
    context: RunContextWrapper[AirlineAgentContext],
) -> None:
    flight_number = f"FLT-{random.randint(100, 999)}"
    context.context.flight_number = flight_number


### QUOTIENT MCP SETUP


async def setup_quotient_mcp():
    """Set up the custom Quotient MCP server connection."""
    quotient_mcp = MCPServerStreamableHttp(
        params={
            "url": "https://mcp.quotientai.co/mcp/",
        },
        name="Quotient MCP Server",
    )
    return quotient_mcp


### AGENTS


async def create_agents_with_mcp():
    """Create agents with MCP server integration."""

    # Set up Quotient MCP server
    quotient_mcp = await setup_quotient_mcp()
    await quotient_mcp.connect()
    print("✅ MCP server connected")

    faq_agent = Agent[AirlineAgentContext](
        name="FAQ Agent",
        handoff_description="A helpful agent that can answer questions about the airline and access external data through Quotient MCP.",
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
        {TOOL_USE_EVAL_PROMPT_PREFIX}
        You are an FAQ agent with access to advanced tools through the Quotient MCP server. 
        If you are speaking to a customer, you probably were transferred to from the triage agent.
        Use the following routine to support the customer:
        # Routine
        1. Identify the last question asked by the customer.
        2. First, try using the MCP tools if they might be relevant to the question.
        3. Use the faq lookup tool for standard airline questions.
        4. If you cannot answer the question, transfer back to the triage agent.""",
        tools=[faq_lookup_tool],
        mcp_servers=[quotient_mcp],
    )

    seat_booking_agent = Agent[AirlineAgentContext](
        name="Seat Booking Agent",
        handoff_description="A helpful agent that can update a seat on a flight and access external systems through Quotient MCP.",
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
        {TOOL_USE_EVAL_PROMPT_PREFIX}
        You are a seat booking agent with access to advanced tools through the Quotient MCP server.
        If you are speaking to a customer, you probably were transferred to from the triage agent.
        Use the following routine to support the customer:
        # Routine
        1. Ask for their confirmation number.
        2. Ask the customer what their desired seat number is.
        3. Use MCP tools if needed to check additional information.
        4. Use the update seat tool to update the seat on the flight.
        If the customer asks a question that is not related to the routine, transfer back to the triage agent.""",
        tools=[update_seat],
        mcp_servers=[quotient_mcp],
    )

    triage_agent = Agent[AirlineAgentContext](
        name="Triage Agent",
        handoff_description="A triage agent that can delegate a customer's request to the appropriate agent and access external data through Quotient MCP.",
        instructions=(
            f"{RECOMMENDED_PROMPT_PREFIX} "
            f"{TOOL_USE_EVAL_PROMPT_PREFIX} "
            "You are a helpful triaging agent with access to the Quotient MCP server tools. "
            "You can use your tools to delegate questions to other appropriate agents. "
            "You can also use MCP tools to help answer questions or gather information before making handoffs."
        ),
        handoffs=[
            faq_agent,
            handoff(agent=seat_booking_agent, on_handoff=on_seat_booking_handoff),
        ],
        mcp_servers=[quotient_mcp],
    )

    faq_agent.handoffs.append(triage_agent)
    seat_booking_agent.handoffs.append(triage_agent)

    return triage_agent, faq_agent, seat_booking_agent, quotient_mcp


### RUN


async def main():
    print("🚀 Setting up agents with Quotient MCP integration...")

    quotient_mcp = None
    try:
        # Create agents with MCP integration
        triage_agent, faq_agent, seat_booking_agent, quotient_mcp = (
            await create_agents_with_mcp()
        )

        current_agent: Agent[AirlineAgentContext] = triage_agent
        input_items: list[TResponseInputItem] = []
        context = AirlineAgentContext()

        # Generate conversation ID for tracing
        conversation_id = uuid.uuid4().hex[:16]

        print(
            "💬 You can now ask questions and the agents will use both built-in tools and your MCP tools."
        )
        print("📝 Try asking about flights, or anything your MCP server can help with!")
        print("-" * 60)

        while True:
            try:
                user_input = input("Enter your message (or 'quit' to exit): ")
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break

                with trace("Customer service with MCP", group_id=conversation_id):
                    input_items.append({"content": user_input, "role": "user"})
                    result = await Runner.run(
                        current_agent, input_items, context=context
                    )

                    for new_item in result.new_items:
                        agent_name = new_item.agent.name
                        if isinstance(new_item, MessageOutputItem):
                            print(
                                f"🤖 {agent_name}: {ItemHelpers.text_message_output(new_item)}"
                            )
                        elif isinstance(new_item, HandoffOutputItem):
                            print(
                                f"🔄 Handed off from {new_item.source_agent.name} to {new_item.target_agent.name}"
                            )
                        elif isinstance(new_item, ToolCallItem):
                            print(f"🔧 {agent_name}: Calling a tool")
                        elif isinstance(new_item, ToolCallOutputItem):
                            print(
                                f"📋 {agent_name}: Tool call output: {new_item.output}"
                            )
                        else:
                            print(
                                f"ℹ️  {agent_name}: Skipping item: {new_item.__class__.__name__}"
                            )

                    input_items = result.to_input_list()
                    current_agent = result.last_agent

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error during conversation: {e}")
                print("🔄 Continuing...")

    except Exception as e:
        print(f"❌ Failed to set up MCP connection: {e}")
        print("💡 Make sure your MCP server at https://mcp.quotientai.co is accessible")
        print("💡 Check if you need authentication headers or the URL is correct")
    finally:
        # Clean up MCP server connection if it exists
        if quotient_mcp is not None:
            try:
                await quotient_mcp.cleanup()
            except Exception:
                pass  # Ignore cleanup errors


if __name__ == "__main__":
    asyncio.run(main())
