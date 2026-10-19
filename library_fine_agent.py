
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent


# =======================================================
# LIBRARY FINE CALCULATOR TOOL
# =======================================================

@tool
def calculate_library_fine(days_overdue: int, book_type: str) -> str:
    """
    Calculate a library fine using the exact book type
    and number of overdue days supplied by the user.

    Supported book types:
    novel, textbook, reference

    Args:
        days_overdue: Number of days the book was overdue.
        book_type: Exact book type stated by the user.

    Returns:
        Fine calculation or a clear error message.
    """

    if days_overdue < 0:
        return "Error: The number of overdue days cannot be negative."

    book_type = book_type.strip().lower()

    fine_rates = {
        "novel": 2,
        "textbook": 5,
        "reference": 10,
    }

    if book_type not in fine_rates:
        return (
            f"Error: Unknown book type '{book_type}'. "
            "Supported book types are novel, textbook, and reference."
        )

    rate = fine_rates[book_type]
    fine = days_overdue * rate

    return (
        f"Fine: Rs. {fine}. "
        f"The {book_type} was {days_overdue} days overdue "
        f"at Rs. {rate} per day."
    )


# =======================================================
# LOCAL QWEN MODEL USING OLLAMA
# =======================================================

model = ChatOllama(
    model="qwen2.5:3b",
    temperature=0,
)


# =======================================================
# SYSTEM PROMPT
# =======================================================

system_prompt = """
You are a Library Helpdesk AI Assistant.

Your job is to help users calculate library fines.

Whenever the user asks about a library fine, overdue charge,
late-return penalty, or amount payable for a late book,
you MUST call the calculate_library_fine tool.

Never calculate or guess a fine yourself.

IMPORTANT BOOK-TYPE RULES:

1. Pass the exact book type stated by the user to the tool.
2. Do not convert, replace, or assume a different book type.
3. If the user says "magazine", pass book_type="magazine".
4. If the user says "comic", pass book_type="comic".
5. Let the tool validate the book type.
6. Supported book types are novel, textbook, and reference.
7. If the tool returns an Error message, clearly explain that
   error to the user. Do not present it as a successful calculation.
8. Do not invent fine rates or unsupported library policies.
9. If the book type or overdue days are missing, ask the user
   for the missing information instead of guessing.
10. Do not claim that a tool was called successfully unless
    the tool actually returned a result.
"""


# =======================================================
# CREATE AGENT
# =======================================================

agent = create_agent(
    model=model,
    tools=[calculate_library_fine],
    system_prompt=system_prompt,
)


# =======================================================
# PRINT MESSAGE TRACE
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

        # Display tool results where available
        if hasattr(message, "type") and message.type == "tool":
            print("Tool Result:", message.content)

        print("-" * 70)


# =======================================================
# MANUAL MODE START SCREEN
# =======================================================

print("=" * 70)
print("       LIBRARY FINE CALCULATOR AGENT")
print("                MANUAL MODE")
print("=" * 70)

print("\nEnter your library fine questions.")

print("\nDemo Fine Rates:")
print("Novel     : Rs. 2 per day")
print("Textbook  : Rs. 5 per day")
print("Reference : Rs. 10 per day")

print("\nSupported book types:")
print("novel, textbook, reference")

print("\nExamples:")
print("A novel was returned 5 days late.")
print("Calculate the fine for a textbook 3 days overdue.")
print("A comic was returned 2 days late.")

print("\nCommands:")
print("trace - Show the message trace of the previous question")
print("exit  - Close the program")

print("=" * 70)
print()


# =======================================================
# MANUAL USER INPUT LOOP
# =======================================================

last_result = None

while True:
    try:
        user_input = input("User: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nAgent: Goodbye!")
        break

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

    # ---------------------------------------------------
    # SEND QUESTION TO AGENT
    # ---------------------------------------------------

    try:
        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ]
            }
        )

        last_result = result

        messages = result.get("messages", [])
        final_answer = messages[-1].content if messages else (
            "No response was returned by the agent."
        )

        # ------------------------------------------------
        # CHECK TOOL CALLS AND TOOL ERRORS
        # ------------------------------------------------

        tool_was_called = False
        tool_results = []

        for message in messages:
            if hasattr(message, "tool_calls") and message.tool_calls:
                tool_was_called = True

            # ToolMessage contains the tool execution result
            if getattr(message, "type", None) == "tool":
                tool_results.append(str(message.content))

        print("\nAgent:", final_answer)

        if tool_was_called:
            print("[OK] Tool was called.")

            errors = [
                output
                for output in tool_results
                if output.strip().lower().startswith("error:")
            ]

            if errors:
                print("\nTool validation error:")
                for error in errors:
                    print(error)
            elif tool_results:
                print("[OK] Tool returned a result.")
            else:
                print(
                    "[!] A tool call was requested, but "
                    "no tool result was found in the message trace."
                )
        else:
            print("[!] Tool was not called.")

        print()

    # ---------------------------------------------------
    # PROGRAM ERROR
    # ---------------------------------------------------

    except Exception as e:
        print("\nProgram Error:", e)
        print(
            "Check that Ollama is running and "
            "the qwen2.5:3b model is installed."
        )
        print()
