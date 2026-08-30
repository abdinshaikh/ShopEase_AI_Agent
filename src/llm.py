from ollama import chat

from config.settings import OLLAMA_MODEL


def call_ollama(messages, tools):
    """
    Call the local Ollama model.
    """

    return chat(
        model=OLLAMA_MODEL,
        messages=messages,
        tools=tools,
        think=False
    )
