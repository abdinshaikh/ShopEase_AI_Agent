
import uuid

import streamlit as st

from src.agent import create_agent, chat_with_shopease


# =========================================================
# Page configuration
# =========================================================

st.set_page_config(
    page_title="ShopEase AI Agent",
    page_icon="🛍️",
    layout="centered"
)


# =========================================================
# Session initialization
# =========================================================

if "agent_graph" not in st.session_state:
    st.session_state.agent_graph = create_agent()


if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]


if "customer_id" not in st.session_state:
    st.session_state.customer_id = ""


if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# Helper functions
# =========================================================

def create_new_conversation():

    st.session_state.session_id = str(uuid.uuid4())[:8]
    st.session_state.messages = []


def get_thread_id():

    customer_id = st.session_state.customer_id.strip()

    if not customer_id:
        return None

    return (
        f"customer_{customer_id}_"
        f"{st.session_state.session_id}"
    )


# =========================================================
# Sidebar
# =========================================================

with st.sidebar:

    st.title("🛍️ ShopEase")

    st.markdown(
        "### AI Customer Support"
    )

    st.divider()

    customer_id = st.text_input(
        "Customer ID",
        value=st.session_state.customer_id,
        placeholder="e.g. C001"
    )

    # Detect customer change
    if customer_id != st.session_state.customer_id:

        st.session_state.customer_id = customer_id
        create_new_conversation()

    st.divider()

    if st.button(
        "➕ New Conversation",
        use_container_width=True
    ):

        create_new_conversation()
        st.rerun()

    st.divider()

    st.caption(
        f"Session: {st.session_state.session_id}"
    )

    if st.session_state.customer_id:

        st.success(
            f"Customer: {st.session_state.customer_id}"
        )

    else:

        st.warning(
            "Enter your Customer ID to start chatting."
        )


# =========================================================
# Main header
# =========================================================

st.title("🛍️ ShopEase AI Customer Support")

st.caption(
    "AI-powered customer support for orders, products, "
    "cancellations, and returns."
)


# =========================================================
# Customer ID validation
# =========================================================

if not st.session_state.customer_id.strip():

    st.info(
        "👈 Enter your Customer ID in the sidebar "
        "to start a conversation."
    )

else:

    st.markdown(
        f"**Customer:** "
        f"{st.session_state.customer_id}"
    )


# =========================================================
# Display conversation
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )


# =========================================================
# Chat input
# =========================================================

user_message = st.chat_input(
    "Ask ShopEase something..."
)


if user_message:

    if not st.session_state.customer_id.strip():

        st.warning(
            "Please enter your Customer ID first."
        )

        st.stop()


    thread_id = get_thread_id()


    # -----------------------------------------------------
    # Customer message
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    with st.chat_message("user"):

        st.markdown(user_message)


    # -----------------------------------------------------
    # Agent response
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "ShopEase is thinking..."
        ):

            response = chat_with_shopease(
                st.session_state.agent_graph,
                user_message,
                thread_id
            )

        st.markdown(response)


    # -----------------------------------------------------
    # Save response to current UI
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )
