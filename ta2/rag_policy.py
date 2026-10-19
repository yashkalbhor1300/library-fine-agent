
"""Deterministic RAG retrieval over the library policy document."""
from __future__ import annotations

import re
from pathlib import Path
from dataclasses import dataclass

POLICY_PATH = Path(__file__).resolve().parent / "docs" / "library_rules.txt"


@dataclass
class PolicyChunk:
    text: str
    score: int


def load_chunks() -> list[str]:
    """Load policy sections separated by blank lines."""
    text = POLICY_PATH.read_text(encoding="utf-8-sig")
    return [
        block.strip()
        for block in re.split(r"\n\s*\n", text)
        if block.strip()
    ]


def retrieve_policy(query: str, top_k: int = 2) -> list[PolicyChunk]:
    """Retrieve relevant rules without matching unrelated common words."""
    query_lower = query.lower()

    book_types = [
        book
        for book in ("novel", "textbook", "reference")
        if re.search(rf"\b{book}\b", query_lower)
    ]

    waiver_requested = any(
        term in query_lower
        for term in ("waive", "waiver", "forgive", "remove the fine")
    )

    # Unsupported requests, such as laptop borrowing fees, must not
    # match merely because they contain common words like "the" or "is".
    if not book_types and not waiver_requested:
        return []

    blocks = load_chunks()
    matches: list[PolicyChunk] = []

    asks_about_loan_period = any(
        term in query_lower
        for term in ("loan", "borrow", "borrowing", "period", "due date")
    )

    asks_about_calculation = any(
        term in query_lower
        for term in ("calculate", "calculation", "how much", "fine")
    )

    for block in blocks:
        lower_block = block.lower()
        score = 0

        if book_types and "fine slabs" in lower_block:
            score = 100

        if (
            book_types
            and asks_about_loan_period
            and "loan periods" in lower_block
        ):
            score = 120

        if (
            book_types
            and asks_about_calculation
            and "fine calculation" in lower_block
        ):
            score = max(score, 80)

        if waiver_requested and "fine waiver" in lower_block:
            score = max(score, 130)

        if score:
            matches.append(PolicyChunk(text=block, score=score))

    matches.sort(key=lambda chunk: chunk.score, reverse=True)
    return matches[:max(1, top_k)]


def retrieve_for_book(book_type: str) -> str:
    hits = retrieve_policy(book_type)
    return (
        "\n\n".join(hit.text for hit in hits)
        if hits
        else "NO_POLICY_MATCH"
    )
