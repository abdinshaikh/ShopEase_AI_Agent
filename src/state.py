from typing import TypedDict, Annotated

from langgraph.graph.message import add_messages


class AgentState(TypedDict):

    messages: Annotated[list, add_messages]

    order_id: str

    tool_result: str

    gemini_interaction_id: str
