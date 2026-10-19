"""Human approval gate for fine waivers."""

def request_human_approval(member_id: str, fine_amount: str, reason: str) -> dict:
    print("\n[HUMAN APPROVAL REQUIRED]")
    print(f"Member: {member_id}")
    print(f"Fine: {fine_amount}")
    print(f"Reason: {reason}")
    answer = input("Librarian approval? [y/N]: ").strip().lower()
    approved = answer in {"y", "yes"}
    return {"approved": approved, "status": "APPROVED" if approved else "DENIED"}
