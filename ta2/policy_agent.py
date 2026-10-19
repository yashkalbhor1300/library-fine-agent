"""Policy agent with RAG retrieval."""
from __future__ import annotations
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from .rag_policy import retrieve_policy

@tool
def retrieve_library_policy(query: str) -> str:
    """Retrieve matching chunks from the library rules document.

    If nothing matches, return NO_POLICY_MATCH. Never invent a missing rule.
    """
    hits = retrieve_policy(query)
    if not hits:
        return "NO_POLICY_MATCH"
    return "\n\n".join(f"[Policy chunk score={h.score}]\n{h.text}" for h in hits)

model = ChatOllama(model="qwen2.5:3b", temperature=0)

policy_agent = create_agent(
    model=model,
    tools=[retrieve_library_policy],
    system_prompt=(
        "You are the Policy Agent. The library rules live in a retrievable document. "
        "Always call retrieve_library_policy before answering a policy question. "
        "Return only rules supported by retrieved text. If the tool says NO_POLICY_MATCH, "
        "say exactly that the policy chunk was not found and do not guess. "
        "Do not perform fine arithmetic; the Calculator Agent does that."
    ),
)
