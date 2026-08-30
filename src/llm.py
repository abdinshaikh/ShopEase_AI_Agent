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
    Convert ShopEase tool definitions into the
    Gemini Interactions API function format.
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


def call_gemini(
    messages,
    tools,
    system_prompt,
    previous_interaction_id=""
):
    """
    Call Gemini through the Interactions API.

    A normal customer message starts a NEW interaction.

    When Gemini requests a tool, LangGraph executes the
    tool and calls this function again with the previous
    Gemini interaction ID and the tool result.
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

    # =====================================================
    # TOOL RESULT CONTINUATION
    # =====================================================

    if previous_interaction_id:

        tool_message = None

        for message in reversed(messages):

            if (
                isinstance(message, dict)
                and message.get("role") == "tool"
            ):

                tool_message = message
                break

        if tool_message is None:

            raise RuntimeError(
                "Expected a tool result when "
                "continuing a Gemini interaction."
            )

        tool_name = tool_message.get(
            "name"
        )

        tool_call_id = tool_message.get(
            "tool_call_id"
        )

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

    # =====================================================
    # NEW CUSTOMER TURN
    # =====================================================

    else:

        user_message = ""

        for message in reversed(messages):

            if not isinstance(
                message,
                dict
            ):
                continue

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

    # =====================================================
    # NORMALIZE GEMINI RESPONSE
    # =====================================================

    content = ""

    tool_calls = []

    steps = response.steps or []

    for step in steps:

        # -------------------------------------------------
        # Function call
        # -------------------------------------------------

        if step.type == "function_call":

            arguments = (
                getattr(
                    step,
                    "arguments",
                    None
                )
                or {}
            )

            tool_name = (
                getattr(
                    step,
                    "name",
                    ""
                )
                or ""
            )

            tool_call_id = (
                getattr(
                    step,
                    "id",
                    ""
                )
                or ""
            )

            tool_calls.append({
                "name": tool_name,
                "args": dict(arguments),
                "id": tool_call_id
            })

        # -------------------------------------------------
        # Model output
        # -------------------------------------------------

        elif step.type == "model_output":

            outputs = (
                getattr(
                    step,
                    "content",
                    None
                )
                or []
            )

            for output in outputs:

                if (
                    getattr(
                        output,
                        "type",
                        None
                    )
                    == "text"
                ):

                    content += (
                        getattr(
                            output,
                            "text",
                            ""
                        )
                        or ""
                    )

    # -----------------------------------------------------
    # Fallback
    # -----------------------------------------------------

    if not content:

        content = (
            getattr(
                response,
                "output_text",
                ""
            )
            or ""
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
