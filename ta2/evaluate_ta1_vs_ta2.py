"""Evidence table for five TA1 vs TA2 cases.

Run from the project root with Ollama running. The table is also documented
in README.md so the architecture can be explained even without execution.
"""
from .supervisor import run_ta2

CASES = [
    ("5 days late novel", "A novel was returned 5 days late."),
    ("5 days late reference", "And if it were a reference book?"),
    ("negative days", "Calculate the fine for a novel returned -3 days late."),
    ("missing policy", "What is the fine for a laptop?"),
    ("waiver", "A novel is 5 days late. Please waive the fine because of an emergency."),
]

print("CASE | TA1 | TA2")
print("-" * 100)
for name, prompt in CASES:
    try:
        result = run_ta2(prompt, thread_id="evaluation", member_id="E001")
        ta2 = result.get("answer", "")
        print(f"{name} | Single calculator agent | {ta2}")
    except Exception as exc:
        print(f"{name} | Single calculator agent | ERROR: {exc}")
