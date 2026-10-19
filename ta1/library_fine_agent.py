from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent


# =======================================================
# LIBRARY FINE CALCULATOR TOOL
# =======================================================

@tool
def calculate_library_fine(days_overdue: int, book_type: str) -> str:
    """
    Calculate a library fine based on the number of overdue days
    and the exact book type provided by the user.

    Use this tool whenever the user asks about a library fine,
    overdue charge, late-return penalty, or amount payable for
    returning a book late.

    Always pass the exact book type stated by the user.

    Supported book types:
    novel, textbook, reference

    Args:
        days_overdue: Number of days the book was returned late.
        book_type: Exact type of book stated by the user.

    Returns:
        Fine amount with explanation,
        or an Error message for invalid input.
    """

    # Check negative days
    if days_overdue < 0:
        return "Error: days_overdue cannot be negative."

    # Normalize book type
    book_type = book_type.lower().strip()

    # Demo fine rates
    fine_rates = {
        "novel": 2,
        "textbook": 5,
        "reference": 10
    }

    # Check book type
    if book_type not in fine_rates:
        return (
            f"Error: Unknown book_type '{book_type}'. "
            "Supported book types are novel, textbook, and reference."
        )

    # Calculate fine
    rate = fine_rates[book_type]
    fine = days_overdue * rate

    return (
        f"Fine: ₹{fine}. "
        f"The {book_type} was {days_overdue} days overdue "
        f"at ₹{rate} per day."
    )


# =======================================================
# LOCAL QWEN MODEL USING OLLAMA
# =======================================================

model = ChatOllama(
    model="qwen2.5:3b",
    temperature=0
)


# =======================================================
# SYSTEM PROMPT
# =======================================================

system_prompt = """
You are a Library Helpdesk AI Assistant.

Your job is to help users calculate library fines.

Whenever the user asks about:
- library fine
- overdue charge
- late-return penalty
- amount payable for a late book

you MUST call the calculate_library_fine tool.

Never calculate or guess the fine yourself.

IMPORTANT:

Pass the exact book type stated by the user to the tool.

Do not convert or replace unsupported book types.

For example:

If the user says magazine,
pass book_type="magazine".

If the user says comic,
pass book_type="comic".

Let the calculate_library_fine tool validate the book type.

Supported book types are:
- novel
- textbook
- reference

If the tool returns an Error message,
clearly explain the error to the user.
"""


# =======================================================
# CREATE AGENT
# =======================================================

agent = create_agent(
    model=model,
    tools=[calculate_library_fine],
    system_prompt=system_prompt
)


# =======================================================
# FUNCTION TO PRINT MESSAGE TRACE
# =======================================================

def print_trace(result):

    print("\n")
    print("=" * 70)
    print("FULL MESSAGE TRACE")
    print("=" * 70)

    for i, message in enumerate(result["messages"], start=1):

        print(f"\nMessage {i}")
        print("Type:", type(message).__name__)

        if hasattr(message, "content"):
            print("Content:", message.content)

        if hasattr(message, "tool_calls") and message.tool_calls:
            print("Tool Calls:", message.tool_calls)

        print("-" * 70)


# =======================================================
# MANUAL MODE START SCREEN
# =======================================================

print("=" * 70)
print("       LIBRARY FINE CALCULATOR AGENT")
print("                MANUAL MODE")
print("=" * 70)

print("\nYou can now enter your own library fine questions.")

print("\nDemo Fine Rates:")
print("Novel     : ₹2 per day")
print("Textbook  : ₹5 per day")
print("Reference : ₹10 per day")

print("\nSupported book types:")
print("novel, textbook, reference")

print("\nCommands:")
print("trace - Show the full message trace of the previous question")
print("exit  - Close the program")

print("=" * 70)
print()


# =======================================================
# MANUAL USER INPUT LOOP
# =======================================================

last_result = None

while True:

    user_input = input("User: ").strip()

    # ---------------------------------------------------
    # EXIT
    # ---------------------------------------------------

    if user_input.lower() in ["exit", "quit"]:

        print("\nAgent: Thank you for using the Library Fine Calculator Agent.")
        print("Agent: Goodbye!")

        break


    # ---------------------------------------------------
    # TRACE COMMAND
    # ---------------------------------------------------

    if user_input.lower() == "trace":

        if last_result is not None:
            print_trace(last_result)
        else:
            print("\nAgent: No previous calculation is available.")

        print()
        continue


    # ---------------------------------------------------
    # EMPTY INPUT
    # ---------------------------------------------------

    if not user_input:

        print("\nAgent: Please enter a library fine question.\n")
        continue


    try:

        # ------------------------------------------------
        # SEND QUESTION TO AGENT
        # ------------------------------------------------

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            }
        )

        # Save result for optional trace
        last_result = result

        # Final AI response
        final_answer = result["messages"][-1].content

        print("\nAgent:", final_answer)


        # ------------------------------------------------
        # CHECK WHETHER TOOL WAS CALLED
        # ------------------------------------------------

        tool_was_called = False

        for message in result["messages"]:

            if hasattr(message, "tool_calls") and message.tool_calls:
                tool_was_called = True


        if tool_was_called:
            print("[✓ Tool was called successfully]")
        else:
            print("[!] Tool was not called.")

        print()


    # ---------------------------------------------------
    # PROGRAM ERROR
    # ---------------------------------------------------

    except Exception as e:

        print("\nProgram Error:", e)

        print(
            "Please make sure Ollama is running "
            "and qwen2.5:3b is installed."
        )

        print()