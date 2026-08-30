import sqlite3


from src.llm import call_llm

from langchain_core.messages import (
    AIMessage,
    ToolMessage,
)

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from langgraph.checkpoint.sqlite import SqliteSaver

from src.state import AgentState

from src.agent_tools import (
    check_order_status_tool,
    get_order_details_tool,
    check_cancellation_eligibility_tool,
    cancel_order_tool,
    get_product_info_tool,
    get_return_policy_tool,
)


from config.settings import (
    MEMORY_DB_PATH,
    LLM_PROVIDER,
    DEBUG_MODE
)


SHOP_EASE_SYSTEM_PROMPT = """
You are the ShopEase customer support assistant.

ShopEase is an online shopping company.

Your job is to help customers with:
- Order status
- Order details
- Order cancellation
- Product information
- Return policy

IMPORTANT RULES:

1. NEVER invent information.
   Only provide information that is available from the tools, conversation, or system instructions.

2. If the requested information is not available, clearly say that it was not found.

3. Do not invent cancellation reasons.
   The order database may contain the status "Cancelled" without containing a cancellation reason.

4. Choose tools based on the customer's actual intent.

TOOL GUIDELINES:

- check_order_status_tool:
  Use when the customer asks where an order is, asks for its current status, or asks whether it has shipped, delivered, or been cancelled.

- get_order_details_tool:
  Use when the customer asks what product is associated with an order, the quantity, price, or other order details.

- check_cancellation_eligibility_tool:
  Use when the customer asks whether an order CAN or CANNOT be cancelled.
  This tool checks whether cancellation is currently possible.

- cancel_order_tool:
  Use when the customer explicitly asks you to CANCEL an order.
  Do not use this tool merely because the customer asks whether cancellation is possible.

- get_product_info_tool:
  Use when the customer asks about a product's price, category, or basic product information.

- get_return_policy_tool:
  Use when the customer asks about ShopEase's return policy, return window, or basic return eligibility requirements.

5. If an order is already cancelled, do not claim that you cancelled it yourself.
   Clearly explain that it was already cancelled.

6. If an order has already shipped, do not claim that it was cancelled.
   Explain that it cannot be cancelled because it has already shipped.

7. When the customer asks a follow-up question such as "Why?", use the previous conversation to understand what they are referring to.

8. If the previous conversation establishes an order ID, use that order ID when appropriate instead of unnecessarily asking the customer to repeat it.

9. Keep responses concise, clear, and friendly.

10. Never expose internal tool names, database details, Python code, or implementation details to the customer.
"""


tools = [
    {
        "type": "function",
        "function": {
            "name": "check_order_status_tool",
            "description": "Check the current status of a ShopEase order using its order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The ShopEase order ID."
                    }
                },
                "required": ["order_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_order_details_tool",
            "description": "Get the product, quantity, price, and status of a ShopEase order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The ShopEase order ID."
                    }
                },
                "required": ["order_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "check_cancellation_eligibility_tool",
            "description": "Check whether a ShopEase order can currently be cancelled.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The ShopEase order ID."
                    }
                },
                "required": ["order_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "cancel_order_tool",
            "description": "Cancel a ShopEase order if it is eligible for cancellation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The ShopEase order ID."
                    }
                },
                "required": ["order_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_product_info_tool",
            "description": "Get the price and category of a ShopEase product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The name of the ShopEase product."
                    }
                },
                "required": ["product_name"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_return_policy_tool",
            "description": "Get the current ShopEase return policy and eligibility requirements.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


tool_functions = {
    "check_order_status_tool": check_order_status_tool,
    "get_order_details_tool": get_order_details_tool,
    "check_cancellation_eligibility_tool": check_cancellation_eligibility_tool,
    "cancel_order_tool": cancel_order_tool,
    "get_product_info_tool": get_product_info_tool,
    "get_return_policy_tool": get_return_policy_tool,
}


def convert_to_ollama_messages(messages):

    converted = []

    for message in messages:

        if hasattr(message, "type"):

            if message.type == "human":
                converted.append({
                    "role": "user",
                    "content": message.content
                })

            elif message.type == "ai":

                msg = {
                    "role": "assistant",
                    "content": message.content or ""
                }

                if message.tool_calls:
                    msg["tool_calls"] = [
                        {
                            "function": {
                                "name": tc["name"],
                                "arguments": tc["args"]
                            }
                        }
                        for tc in message.tool_calls
                    ]

                converted.append(msg)

            elif message.type == "tool":

                converted.append({
                    "role": "tool",
                    "content": message.content,
                    "name": message.name,
                    "tool_call_id": message.tool_call_id
                })

        else:

            converted.append(message)

    return converted


def agent_node(state: AgentState):

    ollama_messages = convert_to_ollama_messages(
        state["messages"]
    )

    messages_for_qwen = [
        {
            "role": "system",
            "content": SHOP_EASE_SYSTEM_PROMPT
        }
    ] + ollama_messages

    response = call_llm(
        provider=LLM_PROVIDER,
        messages=messages_for_qwen,
        tools=tools,
        system_prompt=SHOP_EASE_SYSTEM_PROMPT,
        previous_interaction_id=state.get(
            "gemini_interaction_id",
            ""
        )
    )

    if DEBUG_MODE:
        print("Qwen response:")
        print(response)

    tool_calls = []

    for index, tool_call in enumerate(
        response.tool_calls
    ):

        tool_calls.append({
            "name": tool_call["name"],
            "args": tool_call["args"],
            "id": f"call_{index + 1}",
            "type": "tool_call"
        })


    ai_message = AIMessage(
        content=response.content or "",
        tool_calls=tool_calls
    )

    return {
        "messages": [ai_message],
        "gemini_interaction_id": response.interaction_id
    }


def tool_node(state: AgentState):

    last_message = state["messages"][-1]

    tool_messages = []

    tool_result = ""
    order_id = ""

    for tool_call in last_message.tool_calls:

        tool_name = tool_call["name"]
        arguments = tool_call["args"]
        tool_call_id = tool_call["id"]

        if DEBUG_MODE:
            print("Tool requested:", tool_name)
            print("Arguments:", arguments)

        tool_function = tool_functions[tool_name]

        result = tool_function(**arguments)

        if DEBUG_MODE:
            print("Tool result:", result)

        tool_messages.append(
            ToolMessage(
                content=result,
                name=tool_name,
                tool_call_id=tool_call_id
            )
        )

        tool_result = result

        if "order_id" in arguments:
            order_id = arguments["order_id"]

    return {
        "messages": tool_messages,
        "tool_result": tool_result,
        "order_id": order_id
    }


def agent_router(state: AgentState):

    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage):
        if last_message.tool_calls:
            return "tool"

    return "end"


def create_agent():

    builder = StateGraph(AgentState)

    builder.add_node("agent", agent_node)
    builder.add_node("tool", tool_node)

    builder.add_edge(START, "agent")

    builder.add_conditional_edges(
        "agent",
        agent_router,
        {
            "tool": "tool",
            "end": END
        }
    )

    builder.add_edge("tool", "agent")

    connection = sqlite3.connect(
        MEMORY_DB_PATH,
        check_same_thread=False
    )

    memory = SqliteSaver(connection)

    graph = builder.compile(
        checkpointer=memory
    )

    return graph


def chat_with_shopease(
    agent_graph,
    user_message: str,
    thread_id: str
) -> str:
    """
    Send a customer message to the ShopEase agent.

    The thread_id identifies the conversation and allows
    LangGraph to maintain conversation memory.
    """

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = agent_graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        },
        config=config
    )

    return result["messages"][-1].content
