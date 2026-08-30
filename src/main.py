
import uuid

from src.agent import create_agent, chat_with_shopease


def main():

    print("=" * 60)
    print("        ShopEase AI Customer Support")
    print("=" * 60)

    customer_id = input("Enter customer ID: ").strip()

    if not customer_id:
        print("Customer ID cannot be empty.")
        return

    session_id = str(uuid.uuid4())[:8]

    thread_id = f"customer_{customer_id}_{session_id}"

    print()
    print("Session:", session_id)
    print("Type 'exit' to end the conversation.")
    print()

    agent_graph = create_agent()

    while True:

        user_message = input("CUSTOMER: ")

        if user_message.lower().strip() == "exit":
            print("Goodbye!")
            break

        if not user_message.strip():
            continue

        response = chat_with_shopease(
            agent_graph,
            user_message,
            thread_id
        )

        print()
        print("AGENT:", response)
        print()


if __name__ == "__main__":
    main()
