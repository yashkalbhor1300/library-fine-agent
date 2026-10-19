# Library Fine Agent — TA2 (Unit 3 & 4)

## Architecture

`User -> Supervisor -> Policy Agent (RAG) -> Calculator Agent (tool) -> Supervisor -> optional Human Approval`

The arithmetic stays in `calculate_library_fine`. Policy facts (loan periods, daily fine slabs, waiver rule) come from `ta2/docs/library_rules.txt` through the RAG retriever. The supervisor enforces `MAX_HOPS=6` and stops if no policy chunk is found.

## Unit 3
- Thread memory is stored in SQLite in `ta2/library_ta2.db`.
- Member profile is stored under `(member_id, profile)` conceptually as a SQLite `profiles` table keyed by `member_id`.
- Follow-ups can reuse conversation history.
- RAG retrieves the one-page policy document.

## Unit 4
- Policy Agent: retrieves policy; never performs arithmetic.
- Calculator Agent: calls `calculate_library_fine`; never invents a rate.
- Supervisor: routes between agents and stops after `MAX_HOPS`.
- Human approval: waiver requests cannot be granted automatically.

## Run

1. Install packages from `requirements.txt`.
2. Install/start Ollama and pull the local model:
   `ollama pull qwen2.5:3b`
3. From the project root run:
   `python -m ta2.run_ta2`
4. Try:
   - `A novel was returned 5 days late.`
   - `and if it were a reference book?`
   - `Calculate the fine for a novel returned -3 days late.`
   - `What is the laptop borrowing fee?` (demonstrates missing policy)
   - `A novel is 5 days late. Please waive the fine.` (human approval)

## Evidence to show the jury

### Supervisor routing trace — successful case
`SUPERVISOR -> POLICY_AGENT -> RAG -> CALCULATOR_AGENT -> TOOL -> SUPERVISOR -> FINAL`

Expected result for a novel 5 days late: `Fine: ₹10`.

### Missing policy case
For an unsupported policy such as a laptop borrowing fee, RAG returns no matching chunk. The supervisor stops with:
`I could not find a matching rule in the library policy document, so I will not invent one.`

### 5-case TA1 vs TA2 comparison

| Case | TA1 | TA2 evidence |
|---|---|---|
| 5 days late novel | Calculates fine with one tool agent | Policy RAG -> Calculator tool -> final |
| Follow-up reference | Needs days repeated in a fresh call | Thread memory can retain previous context |
| -3 days | Tool returns clear Error | Same calculator error, routed through supervisor |
| Missing policy | No policy/RAG layer | Explicit missing-chunk stop; no invented rule |
| Waiver request | No human gate | Supervisor routes to human approval before waiver |

## Jury answers

**Does the policy live in RAG and arithmetic in the tool?** Yes. The RAG layer retrieves rules from `library_rules.txt`; the calculator tool performs multiplication and validates inputs.

**What does the supervisor do if Policy Agent finds no matching rule?** It stops the route and says the policy chunk was not found. It does not invent a rule or send the request to the calculator.

**What happens when the calculator returns an Error string?** The Calculator Agent receives the tool result and reports the error clearly; the system does not treat it as a valid fine.
