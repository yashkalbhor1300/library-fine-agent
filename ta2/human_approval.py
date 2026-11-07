"""Fail-closed, request-specific human approval for demo fine waivers."""
from __future__ import annotations

from typing import Callable


def request_human_approval(
    member_id: str,
    fine_amount: str,
    reason: str,
    request_id: str,
    input_fn: Callable[[str], str] | None = None,
) -> dict:
    """Require an exact confirmation phrase for this specific waiver request.

    This interactive gate is a demo safeguard, not identity authentication.
    """
    if not request_id or not request_id.strip():
        raise ValueError("A request ID is required for human approval.")

    print("\n[HUMAN APPROVAL REQUIRED]")
    print("Review the exact action before deciding:")
    print(f"Request ID: {request_id}")
    print(f"Member: {member_id}")
    print(f"Fine to waive: ₹{fine_amount}")
    print(f"Reason: {reason}")
    print("This records a local demo event only; no live account is changed.")

    read_input = input_fn or input
    expected = f"APPROVE {request_id}"
    answer = read_input(
        f'Type "{expected}" exactly to approve; anything else denies: '
    ).strip()

    approved = answer == expected
    return {
        "request_id": request_id,
        "approved": approved,
        "status": "APPROVED" if approved else "DENIED",
        "approval_method": "exact_interactive_confirmation",
        "authenticated_identity": False,
    }
