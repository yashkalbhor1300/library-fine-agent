"""Interactive TA2 runner."""
from .supervisor import run_ta2
from .profile_store import ProfileStore

print("=" * 72)
print("LIBRARY FINE AGENT — TA2 MULTI-AGENT DEMO")
print("=" * 72)
print("Thread memory is persistent in ta2/library_ta2.db")
print("Commands: trace, profile, exit")
print()

thread_id = input("Thread ID [demo-thread]: ").strip() or "demo-thread"
member_id = input("Member ID [M001]: ").strip() or "M001"
ProfileStore().save_profile(member_id, {"member_id": member_id, "name": "Demo Member"})
last = None

while True:
    q = input("User: ").strip()
    if q.lower() in {"exit", "quit"}:
        break
    if not q:
        continue
    if q.lower() == "trace":
        print("\nSupervisor routing trace:")
        print(" -> ".join(last.get("trace", [])) if last else "No trace yet.")
        continue
    if q.lower() == "profile":
        print(ProfileStore().get_profile(member_id))
        continue
    try:
        last = run_ta2(q, thread_id=thread_id, member_id=member_id)
        print("\nAgent:", last.get("answer", ""))
        print("Policy found:", last.get("policy_found"))
        print("Trace:", " -> ".join(last.get("trace", [])))
    except Exception as exc:
        print("\nProgram Error:", exc)
        print("Make sure Ollama is running and qwen2.5:3b is installed.")
