
import uuid

from src.agent import create_agent, chat_with_shopease


def run_agent(message):

    graph = create_agent()

    thread_id = (
        f"pytest_agent_{uuid.uuid4().hex[:8]}"
    )

    return chat_with_shopease(
        graph,
        message,
        thread_id
    )


def test_agent_order_status():

    response = run_agent(
        "Where is order 12345?"
    )

    response_lower = response.lower()

    assert "12345" in response
    assert "shipped" in response_lower


def test_agent_product_information():

    response = run_agent(
        "What is the price of the Laptop?"
    )

    normalized_response = (
        response
        .replace(",", "")
        .replace("₹", "")
        .replace(" ", "")
    )

    assert "65000" in normalized_response


def test_agent_return_policy():

    response = run_agent(
        "What is your return policy?"
    )

    response_lower = response.lower()

    assert "30 days" in response_lower
    assert "original packaging" in response_lower


def test_agent_unknown_order():

    response = run_agent(
        "Where is order 99999?"
    )

    response_lower = response.lower()

    assert (
        "not found" in response_lower
        or "does not exist" in response_lower
        or "no record" in response_lower
        or "couldn't find" in response_lower
        or "could not find" in response_lower
    )
