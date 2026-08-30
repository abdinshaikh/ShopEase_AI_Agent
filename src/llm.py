import os

from dataclasses import dataclass, field

from ollama import chat

from google import genai

from config.settings import (
    OLLAMA_MODEL,
    GEMINI_MODEL
)


@dataclass
class LLMResponse:
    """
    Common response format used by the ShopEase agent.
    """

    content: str = ""

    tool_calls: list = field(
        default_factory=list
    )

    interaction_id: str = ""


# =========================================================
# Ollama
# =========================================================

def call_ollama(
    messages,
    tools
):
    """
    Call the local Ollama model and normalize its response.
    """

    response = chat(
        model=OLLAMA_MODEL,
        messages=messages,
        tools=tools,
        think=False
    )

    tool_calls = []

    if response.message.tool_calls:

        for tool_call in response.message.tool_calls:

            tool_calls.append({
                "name": tool_call.function.name,
                "args": tool_call.function.arguments
            })

    return LLMResponse(
        content=response.message.content or "",
        tool_calls=tool_calls
    )


# =========================================================
# Gemini helpers
# =========================================================

def _convert_tools_to_gemini(
    tools
):
    """
    Convert ShopEase's existing tool definitions
    into Interactions API function definitions.
    """

    gemini_tools = []

    for tool in tools:

        function = tool["function"]

        gemini_tools.append({
            "type": "function",
            "name": function["name"],
            "description": function["description"],
            "parameters": function["parameters"]
        })

    return gemini_tools


def _convert_messages_to_gemini(
    messages
):
    """
    Convert the application's messages into the
    Interactions API input format.
    """

    converted = []

    for message in messages:

        role = message.get("role")

        content = message.get(
            "content",
            ""
        )

        # -------------------------------------------------
        # System messages
        # -------------------------------------------------

        if role == "system":
            continue

        # -------------------------------------------------
        # User messages
        # -------------------------------------------------

        if role == "user":

            if content:

                converted.append({
                    "type": "text",
                    "role": "user",
                    "text": content
                })

        # -------------------------------------------------
        # Assistant messages
        # -------------------------------------------------

        elif role == "assistant":

            if content:

                converted.append({
                    "type": "text",
                    "role": "model",
                    "text": content
                })

            for tool_call in message.get(
                "tool_calls",
                []
            ):

                function = tool_call["function"]

                converted.append({
                    "type": "function_call",
                    "name": function["name"],
                    "arguments": function["arguments"],
                    "call_id": tool_call["id"]
                })

        # -------------------------------------------------
        # Tool results
        # -------------------------------------------------

        elif role == "tool":

            tool_name = message.get(
                "name",
                "unknown_tool"
            )

            tool_call_id = message.get(
                "tool_call_id",
                ""
            )

            if content:

                converted.append({
                    "type": "function_result",
                    "name": tool_name,
                    "call_id": tool_call_id,
                    "result": [
                        {
                            "type": "text",
                            "text": content
                        }
                    ]
                })

    return converted


# =========================================================
# Gemini
# =========================================================

def call_gemini(
    messages,
    tools,
    system_prompt,
    previous_interaction_id=""
):
    """
    Call Gemini through the Interactions API.

    The first call sends the user's message and tools.

    When a tool has been executed by LangGraph, the second
    call sends only the corresponding function result using
    the previous Gemini interaction ID.
    """

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(
        api_key=api_key
    )

    gemini_tools = (
        _convert_tools_to_gemini(
            tools
        )
    )

    # -----------------------------------------------------
    # Continue an existing Gemini interaction
    # -----------------------------------------------------

    if previous_interaction_id:

        tool_message = None

        for message in reversed(messages):

            if hasattr(message, "type"):

                if message.type == "tool":
                    tool_message = message
                    break

            elif isinstance(message, dict):

                if message.get("role") == "tool":
                    tool_message = message
                    break

        if tool_message is None:

            raise RuntimeError(
                "No tool result found for the "
                "Gemini interaction."
            )

        if hasattr(tool_message, "name"):

            tool_name = tool_message.name

        else:

            tool_name = tool_message.get(
                "name"
            )

        if hasattr(
            tool_message,
            "tool_call_id"
        ):

            tool_call_id = (
                tool_message.tool_call_id
            )

        else:

            tool_call_id = tool_message.get(
                "tool_call_id"
            )

        if hasattr(
            tool_message,
            "content"
        ):

            tool_content = (
                tool_message.content
            )

        else:

            tool_content = tool_message.get(
                "content",
                ""
            )

        if not tool_name:

            raise RuntimeError(
                "Tool result is missing its tool name."
            )

        if not tool_call_id:

            raise RuntimeError(
                "Tool result is missing its call ID."
            )

        function_result = {
            "type": "function_result",
            "name": tool_name,
            "call_id": tool_call_id,
            "result": [
                {
                    "type": "text",
                    "text": str(tool_content)
                }
            ]
        }

        response = client.interactions.create(
            model=GEMINI_MODEL,
            previous_interaction_id=(
                previous_interaction_id
            ),
            input=[
                function_result
            ]
        )

    # -----------------------------------------------------
    # Start a new Gemini interaction
    # -----------------------------------------------------

    else:

        user_message = ""

        for message in reversed(messages):

            if message.get("role") == "user":

                user_message = message.get(
                    "content",
                    ""
                )

                break

        if not user_message:

            raise RuntimeError(
                "No user message found."
            )

        response = client.interactions.create(
            model=GEMINI_MODEL,
            input=user_message,
            system_instruction=system_prompt,
            tools=gemini_tools
        )

    # -----------------------------------------------------
    # Normalize Gemini response
    # -----------------------------------------------------

    content = ""

    tool_calls = []

    for step in response.steps:

        if step.type == "function_call":

            tool_calls.append({
                "name": step.name,
                "args": dict(
                    step.arguments
                ),
                "id": step.id
            })

        elif step.type == "text":

            if hasattr(
                step,
                "text"
            ):

                content += (
                    step.text or ""
                )

    if not content:

        content = (
            response.output_text or ""
        )

    return LLMResponse(
        content=content,
        tool_calls=tool_calls,
        interaction_id=response.id
    )


# =========================================================
# Common interface
# =========================================================

def call_llm(
    provider,
    messages,
    tools,
    system_prompt,
    previous_interaction_id=""
):
    """
    Call the configured LLM provider.
    """

    if provider == "ollama":

        return call_ollama(
            messages,
            tools
        )

    if provider == "gemini":

        return call_gemini(
            messages,
            tools,
            system_prompt,
            previous_interaction_id
        )

    raise ValueError(
        f"Unsupported LLM provider: {provider}"
    )
