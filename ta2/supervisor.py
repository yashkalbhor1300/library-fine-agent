
"""Supervisor graph for the Library Fine Agent."""
from __future__ import annotations

import re
from typing import TypedDict, Any

from langgraph.graph import StateGraph, END

from .policy_agent import retrieve_library_policy
from .calculator_agent import calculate_library_fine
from .human_approval import request_human_approval
from .memory_agent import ThreadMemory
from .profile_store import ProfileStore


MAX_HOPS = 6


class TA2State(TypedDict, total=False):
    thread_id: str
    member_id: str
    user_input: str
    history: str
    policy: str
    policy_found: bool
    calculator_result: str
    answer: str
    waiver_requested: bool
    approval: dict[str, Any]
    hops: int
    trace: list[str]


memory = ThreadMemory()
profiles = ProfileStore()


def _trace(state: TA2State, label: str) -> list[str]:
    return state.get("trace", []) + [label]


def supervisor_node(state: TA2State) -> TA2State:
    hops = state.get("hops", 0) + 1
    if hops > MAX_HOPS:
        return {
            **state,
            "hops": hops,
            "answer": "Error: maximum supervisor hops reached.",
            "trace": _trace(state, "MAX_HOPS_STOP"),
        }
    return {
        **state,
        "hops": hops,
        "trace": _trace(state, "SUPERVISOR -> POLICY"),
    }


def policy_node(state: TA2State) -> TA2State:
    retrieved = retrieve_library_policy.invoke(
        {"query": state["user_input"]}
    )
    policy_text = str(retrieved).strip()
    found = bool(policy_text) and policy_text != "NO_POLICY_MATCH"

    return {
        **state,
        "policy": policy_text,
        "policy_found": found,
        "trace": _trace(state, "POLICY_AGENT -> RAG"),
    }


def route_after_policy(state: TA2State) -> str:
    return "calculator" if state.get("policy_found") else "missing"


def missing_node(state: TA2State) -> TA2State:
    return {
        **state,
        "answer": (
            "I could not find a matching rule in the library policy "
            "document, so I will not invent one."
        ),
        "trace": _trace(
            state, "SUPERVISOR -> POLICY_MISSING -> STOP"
        ),
    }


def calculator_node(state: TA2State) -> TA2State:
    current_request = state["user_input"]
    lower_request = current_request.lower()
    policy_text = state.get("policy", "")

    # Reject negative overdue days before any calculation.
    if re.search(r"(?<!\w)-\s*\d+\s*(?:days?|d)\b", lower_request):
        return {
            **state,
            "calculator_result": (
                "Error: The number of overdue days cannot be negative. "
                "Please provide a valid non-negative number of days."
            ),
            "waiver_requested": False,
            "trace": _trace(
                state, "CALCULATOR_AGENT -> VALIDATION_ERROR"
            ),
        }

    # Use an explicit day count from the current request if present.
    day_match = re.search(
        r"\b(\d+)\s*(?:days?|d)\b", lower_request
    )

    if day_match:
        days = int(day_match.group(1))
    else:
        # Follow-up questions may inherit the last explicit day count.
        history = state.get("history", "")
        prior_days = re.findall(
            r"\b(\d+)\s*(?:days?|d)\b", history.lower()
        )
        if not prior_days:
            return {
                **state,
                "calculator_result": (
                    "Error: Please specify the number of overdue days."
                ),
                "waiver_requested": False,
                "trace": _trace(
                    state, "CALCULATOR_AGENT -> VALIDATION_ERROR"
                ),
            }
        days = int(prior_days[-1])

    # Prefer a book type explicitly named in the current request.
    book_type = next(
        (
            candidate
            for candidate in ("novel", "textbook", "reference")
            if candidate in lower_request
        ),
        None,
    )

    if book_type is None:
        history = state.get("history", "").lower()
        book_type = next(
            (
                candidate
                for candidate in ("novel", "textbook", "reference")
                if candidate in history
            ),
            None,
        )

    if book_type is None:
        return {
            **state,
            "calculator_result": (
                "Error: Please specify novel, textbook, or reference book."
            ),
            "waiver_requested": False,
            "trace": _trace(
                state, "CALCULATOR_AGENT -> VALIDATION_ERROR"
            ),
        }

    # Read the daily rate from the policy retrieved for this request.
    rate_match = re.search(
        rf"\b{re.escape(book_type)}\s*:\s*₹?\s*(\d+)\s*"
        rf"(?:per\s+overdue\s+day|per\s+day)\b",
        policy_text,
        re.IGNORECASE,
    )

    if not rate_match:
        return {
            **state,
            "calculator_result": (
                f"Error: The daily fine rate for {book_type} "
                "was not found in the retrieved policy."
            ),
            "waiver_requested": False,
            "trace": _trace(
                state, "CALCULATOR_AGENT -> VALIDATION_ERROR"
            ),
        }

    daily_rate = int(rate_match.group(1))

    # Call the tool directly with fresh arguments; do not reuse LLM output.
    calculator_result = calculate_library_fine.invoke(
        {
            "days_overdue": days,
            "book_type": book_type,
            "daily_rate": daily_rate,
        }
    )

    waiver_requested = any(
        phrase in lower_request
        for phrase in (
            "waive",
            "waiver",
            "forgive",
            "remove the fine",
        )
    )

    return {
        **state,
        "calculator_result": str(calculator_result),
        "waiver_requested": waiver_requested,
        "trace": _trace(state, "CALCULATOR_AGENT -> TOOL"),
    }


def route_after_calculator(state: TA2State) -> str:
    result = state.get("calculator_result", "").lower()

    if result.startswith("error:"):
        return "finish"

    if state.get("waiver_requested"):
        return "approval"

    return "finish"


def approval_node(state: TA2State) -> TA2State:
    approval = request_human_approval(
        state.get("member_id", "unknown"),
        state.get("calculator_result", ""),
        state["user_input"],
    )

    approved = approval.get("approved", False)
    status = (
        "APPROVED by human librarian."
        if approved
        else "NOT APPROVED; no waiver was granted."
    )

    return {
        **state,
        "approval": approval,
        "answer": (
            f"{state.get('calculator_result', '')}\n"
            f"Waiver status: {status}"
        ),
        "trace": _trace(
            state,
            "HUMAN_APPROVAL -> "
            + str(approval.get("status", "COMPLETED")),
        ),
    }


def finish_node(state: TA2State) -> TA2State:
    return {
        **state,
        "answer": state.get("calculator_result", ""),
        "trace": _trace(state, "SUPERVISOR -> FINAL"),
    }


def build_graph():
    graph_builder = StateGraph(TA2State)

    graph_builder.add_node("supervisor", supervisor_node)
    graph_builder.add_node("policy", policy_node)
    graph_builder.add_node("missing", missing_node)
    graph_builder.add_node("calculator", calculator_node)
    graph_builder.add_node("approval", approval_node)
    graph_builder.add_node("finish", finish_node)

    graph_builder.set_entry_point("supervisor")
    graph_builder.add_edge("supervisor", "policy")

    graph_builder.add_conditional_edges(
        "policy",
        route_after_policy,
        {"calculator": "calculator", "missing": "missing"},
    )

    graph_builder.add_conditional_edges(
        "calculator",
        route_after_calculator,
        {"approval": "approval", "finish": "finish"},
    )

    graph_builder.add_edge("missing", END)
    graph_builder.add_edge("approval", END)
    graph_builder.add_edge("finish", END)

    return graph_builder.compile()


graph = build_graph()


def run_ta2(
    user_input: str,
    thread_id: str = "demo-thread",
    member_id: str = "M001",
) -> dict:
    old = memory.get(thread_id)
    profile = profiles.get_profile(member_id)
    history = old.get("history", "")

    state: TA2State = {
        "thread_id": thread_id,
        "member_id": member_id,
        "user_input": user_input,
        "history": history,
        "hops": 0,
        "trace": [],
    }

    result = graph.invoke(state)

    new_history = (
        history
        + f"\nUser: {user_input}"
        + f"\nAssistant: {result.get('answer', '')}"
    ).strip()

    memory.update(
        thread_id,
        history=new_history,
        last_days=old.get("last_days"),
        last_book_type=old.get("last_book_type"),
    )

    result["profile"] = profile
    return result
