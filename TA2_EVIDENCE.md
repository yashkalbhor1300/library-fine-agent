# TA2 Jury Evidence — One-Page Trace

## Successful case: novel returned 5 days late

**HumanMessage**
> A novel was returned 5 days late.

**Supervisor**
> Routes to Policy Agent. MAX_HOPS = 6.

**Policy Agent / RAG**
> Retrieves the policy chunk containing: Novel = ₹2 per overdue day.

**Calculator Agent**
> Receives the retrieved policy context and calls `calculate_library_fine(days_overdue=5, book_type="novel")`.

**ToolMessage**
> `Fine: ₹10. The novel was 5 days overdue at ₹2 per day.`

**Final answer**
> Fine: ₹10. The novel was 5 days overdue at ₹2 per day.

**Routing trace**
`SUPERVISOR -> POLICY_AGENT -> RAG -> CALCULATOR_AGENT -> TOOL -> SUPERVISOR -> FINAL`

## Deliberate missing-policy case

**HumanMessage**
> What is the laptop borrowing fee?

**RAG result**
> `NO_POLICY_MATCH`

**Supervisor**
> Stops routing. It does not send an unsupported rule to the calculator.

**Final answer**
> I could not find a matching rule in the library policy document, so I will not invent one.

## Jury points

1. **Policy vs arithmetic:** RAG owns policy facts; `calculate_library_fine` owns arithmetic and validation.
2. **Supervisor:** controls routing and enforces `MAX_HOPS`.
3. **Missing policy:** explicit stop rather than hallucinating a rule.
4. **Waiver:** the operator must type `APPROVE <request_id>` exactly; generic `yes` and mismatched request IDs are denied. A matching approval is recorded once in a local SQLite demo audit ledger. This is not identity authentication and does not change a live fine record.
5. **Memory:** SQLite thread memory lets a follow-up reuse earlier conversation context.


## Waiver safety boundary

An approved waiver in this repository is a **simulated** waiver event. The app records the request ID, member ID, fine amount, reason, approval method, and UTC timestamp in the local `waiver_events` table. It does not connect to a production library account, change an actual balance, or process a payment. The interactive phrase is not identity authentication.

## Automated safety tests

Run `python -m unittest discover -s tests -v` from the repository root. Tests cover exact request-specific confirmation, generic-yes denial, mismatched request denial, refusal to write without approval, successful audit recording, and duplicate request rejection.
