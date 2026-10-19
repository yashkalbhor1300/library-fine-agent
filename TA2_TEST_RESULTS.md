\# Library Fine Agent — TA2 Test Results



\## 1. Overview



The Library Fine Agent TA2 application was executed locally using Python 3.11 and a virtual environment. The following functional scenarios were tested through the interactive command-line application.



\## 2. Test Cases



| Test ID | Test Scenario | Input | Observed Result | Status |

|---|---|---|---|---|

| TC-01 | Fine calculation | A novel was returned 5 days late. | Fine calculated as ₹10 at ₹2 per day. Policy found: True. | PASS |

| TC-02 | Contextual follow-up | And if it were a reference book? | Fine calculated as ₹50 at ₹10 per day, using the previous context. | PASS |

| TC-03 | Negative input validation | Calculate the fine for a novel returned -3 days late. | The application rejected negative overdue days. | PASS |

| TC-04 | Missing policy handling | What is the laptop borrowing fee? | The agent reported that no matching library policy rule was found and refused to invent a fee. | PASS |

| TC-05 | Human approval | A novel is 5 days late. Please waive the fine. | The application requested librarian approval. After entering `y`, it reported that the waiver was approved by a human librarian. | PASS — APPROVAL PATH |



\## 3. Technologies and Components Verified



\- Python 3.11 virtual environment

\- LangGraph-based agent workflow

\- Supervisor and policy-agent routing

\- Retrieval-Augmented Generation (RAG) policy lookup

\- Calculator tool for fine calculation

\- Contextual follow-up handling

\- Negative overdue-day validation

\- Human approval checkpoint



\## 4. Example Calculation



For a novel returned five days late:



Fine = Number of overdue days × Fine per day



Fine = 5 × ₹2 = ₹10



For a reference book returned five days late:



Fine = 5 × ₹10 = ₹50



\## 5. Human Approval Observation



The waiver request triggered the human approval checkpoint. After the librarian response `y`, the application displayed:



`Waiver status: APPROVED by human librarian.`



The output continued to display the calculated fine of ₹10. Whether approval also changes the amount due should be verified against the intended waiver policy and implementation.



\## 6. Conclusion



The five tested scenarios produced the expected behavior for fine calculation, contextual follow-up, invalid input rejection, missing-policy handling, and the human approval checkpoint.



These results reflect the local test outputs observed during execution. Additional testing, including the librarian rejection path, is recommended.



