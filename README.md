# ShopEase AI Customer Support

ShopEase is a small AI customer support application built with Python, LangGraph, Ollama, Qwen 3:8B, Streamlit, and SQLite.

The agent can handle common customer support questions about orders, products, cancellations, and returns. It can also remember the conversation within a session.

## What it can do

- Check the status of an order
- Get order details such as product, quantity, price, and status
- Check whether an order can be cancelled
- Cancel an eligible order
- Get basic product information
- Answer questions about the return policy
- Keep conversation context using LangGraph memory

## Tech Stack

- Python
- Streamlit
- LangGraph
- Ollama
- Qwen 3:8B
- SQLite
- Pytest

## How it works

The customer interacts with the Streamlit interface. The message is passed to the LangGraph agent, which uses Qwen 3:8B to understand the request and decide whether a tool is needed.

For example:

Customer:

    Where is order 12345?

The agent selects the order status tool, which checks the SQLite database and returns the current status.

The result is then given back to Qwen, which produces the final response for the customer.

The main flow is:

    Customer → Streamlit → LangGraph → Qwen → Tool → SQLite → Qwen → Response

## Available tools

### Order tools

- `check_order_status_tool`
- `get_order_details_tool`
- `check_cancellation_eligibility_tool`
- `cancel_order_tool`

### Other tools

- `get_product_info_tool`
- `get_return_policy_tool`

The agent is instructed not to make up information that is not available from the database, tools, or system instructions.

## Conversation Memory

LangGraph uses SQLite checkpointing to keep conversation state.

Each conversation gets its own thread ID based on the customer ID and session ID.

The memory database is stored locally as:

    database/agent_memory.db

The database files are not included in the GitHub repository.

## Project Structure

    ShopEase_AI_Agent/
    │
    ├── app.py
    ├── requirements.txt
    ├── .gitignore
    │
    ├── config/
    │   ├── __init__.py
    │   └── settings.py
    │
    ├── src/
    │   ├── __init__.py
    │   ├── agent.py
    │   ├── agent_tools.py
    │   ├── database.py
    │   ├── main.py
    │   ├── policy_data.py
    │   ├── product_data.py
    │   ├── state.py
    │   └── tools.py
    │
    └── tests/
        ├── __init__.py
        ├── test_agent.py
        └── test_tools.py

## Running the project

### 1. Install the Python dependencies

    pip install -r requirements.txt

### 2. Install and run Ollama

The application currently uses Ollama to run Qwen 3:8B locally.

Make sure the model is available:

    ollama pull qwen3:8b

Then make sure Ollama is running.

### 3. Start the Streamlit application

From the project directory:

    streamlit run app.py

The application will open in the browser.

## Testing

The project currently has tests for both the individual tools and the AI agent.

Run all tests with:

    pytest -v

Current test result:

    12 passed

The tool tests use temporary SQLite databases so that the actual ShopEase database is not modified during testing.

## Database

The order database contains the following fields:

    order_id
    customer_id
    product
    quantity
    price
    status

The actual SQLite databases are kept outside the GitHub repository and are ignored using `.gitignore`.

## Current setup

The application currently runs Qwen 3:8B through Ollama. The model and application are running in the same environment during development.

This project is still being developed, so the deployment setup may change later.
