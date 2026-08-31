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

    Supports:
    1. First user turn
    2. Normal subsequent user turns
    3. Tool-result continuation
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
    # Find the latest user/tool message
    # =====================================================

    latest_message = None

    for message in reversed(messages):

        if not isinstance(
            message,
            dict
        ):
            continue

        role = message.get(
            "role"
        )

        if role in (
            "user",
            "tool"
        ):

            latest_message = message
            break

    if latest_message is None:

        raise RuntimeError(
            "No user or tool message found."
        )

    latest_role = latest_message.get(
        "role"
    )

    # =====================================================
    # CASE 1:
    # Tool result continuation
    # =====================================================

    if (
        previous_interaction_id
        and latest_role == "tool"
    ):

        tool_name = latest_message.get(
            "name"
        )

        tool_call_id = (
            latest_message.get(
                "tool_call_id"
            )
        )

        tool_content = (
            latest_message.get(
                "content",
                ""
            )
        )

        if not tool_name:

            raise RuntimeError(
                "Tool result is missing "
                "its tool name."
            )

        if not tool_call_id:

            raise RuntimeError(
                "Tool result is missing "
                "its call ID."
            )

        function_result = {
            "type": "function_result",
            "name": tool_name,
            "call_id": tool_call_id,
            "result": [
                {
                    "type": "text",
                    "text": str(
                        tool_content
                    )
                }
            ]
        }

        response = (
            client.interactions.create(
                model=GEMINI_MODEL,
                previous_interaction_id=(
                    previous_interaction_id
                ),
                input=[
                    function_result
                ]
            )
        )

    # =====================================================
    # CASE 2:
    # Normal subsequent user turn
    # =====================================================

    elif (
        previous_interaction_id
        and latest_role == "user"
    ):

        user_message = (
            latest_message.get(
                "content",
                ""
            )
        )

        if not user_message:

            raise RuntimeError(
                "User message is empty."
            )

        response = (
            client.interactions.create(
                model=GEMINI_MODEL,
                previous_interaction_id=(
                    previous_interaction_id
                ),
                input=user_message,
                tools=gemini_tools
            )
        )

    # =====================================================
    # CASE 3:
    # First user turn
    # =====================================================

    else:

        user_message = (
            latest_message.get(
                "content",
                ""
            )
        )

        if not user_message:

            raise RuntimeError(
                "User message is empty."
            )

        response = (
            client.interactions.create(
                model=GEMINI_MODEL,
                input=user_message,
                system_instruction=system_prompt,
                tools=gemini_tools
            )
        )

    # =====================================================
    # Normalize Gemini response
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
