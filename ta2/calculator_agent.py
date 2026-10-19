
"""Calculator agent: deterministic fine calculation tool."""
from __future__ import annotations

from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent


@tool
def calculate_library_fine(
    days_overdue: int,
    book_type: str,
    daily_rate: int,
) -> str:
    """Calculate a fine using the daily rate retrieved from library policy."""

    if days_overdue < 0:
        return "Error: days_overdue cannot be negative."

    normalized = book_type.lower().strip()
    if normalized not in {"novel", "textbook", "reference"}:
        return f"Error: Unsupported book type '{normalized}'."

    if daily_rate <= 0:
        return "Error: A valid daily rate is required."

    fine = days_overdue * daily_rate
    return (
        f"Fine: ₹{fine}. The {normalized} was {days_overdue} days "
        f"overdue at ₹{daily_rate} per day."
    )


model = ChatOllama(model="qwen2.5:3b", temperature=0)

calculator_agent = create_agent(
    model=model,
    tools=[calculate_library_fine],
    system_prompt=(
        "You are the Calculator Agent. Call calculate_library_fine "
        "for every fine calculation. Use the daily rate supplied from "
        "the retrieved policy. Never reuse a previous result. "
        "If the tool returns an error, report it clearly."
    ),
)
