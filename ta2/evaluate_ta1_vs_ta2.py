
"""TA1 baseline versus TA2 evaluation scenarios.

TA1 is listed as the baseline implementation.
TA2 is executed for each scenario.

Run from the project root:
    python -m ta2.evaluate_ta1_vs_ta2
"""

from ta2.supervisor import run_ta2


CASES = [
    (
        "5 days late novel",
        "A novel was returned 5 days late.",
    ),
    (
        "5 days late reference",
        "A reference book was returned 5 days late.",
    ),
    (
        "Negative overdue days",
        "Calculate the fine for a novel returned -3 days late.",
    ),
    (
        "Unsupported book type",
        "What is the fine for a laptop?",
    ),
    (
        "Waiver request",
        "A novel is 5 days late. Please waive the fine because of an emergency.",
    ),
]


def main():
    print("=" * 110)
    print("LIBRARY FINE AGENT — TA1 BASELINE / TA2 SCENARIO EVALUATION")
    print("=" * 110)
    print(
        "Note: This script executes TA2. "
        "The TA1 column identifies the baseline design; "
        "it does not execute TA1."
    )
    print()

    for name, prompt in CASES:
        print("-" * 110)
        print(f"Scenario: {name}")
        print(f"Input: {prompt}")
        print("TA1: Baseline single-agent implementation (not executed by this script)")

        try:
            result = run_ta2(
                prompt,
                thread_id="evaluation",
                member_id="E001",
            )

            answer = result.get("answer", "No answer returned.")
            print(f"TA2: {answer}")

            if result.get("policy_found") is not None:
                print(f"Policy found: {result['policy_found']}")

            if result.get("trace"):
                print(f"Trace: {result['trace']}")

        except Exception as exc:
            print(f"TA2 execution error: {exc}")

        print()

    print("=" * 110)
    print("Evaluation scenarios completed.")
    print("=" * 110)


if __name__ == "__main__":
    main()
