# Library Fine Agent — TA2
### RAG-Powered Multi-Agent System | Agentic AI — Units 3 & 4

A Python-based multi-agent system that calculates library fines using policy retrieval, tool-based arithmetic, conversation memory, member profiles, and human approval for waiver requests.

**GitHub Repository:** [Library Fine Agent](https://github.com/yashkalbhor1300/library-fine-agent)

---

## 1. Project Overview

The Library Fine Agent demonstrates how multiple specialized agents can collaborate to answer library-related queries while following defined library policies.

Instead of allowing a language model to invent fine rates, the system retrieves relevant rules from a library policy document and delegates arithmetic to a dedicated calculator tool.

### Objectives

- Retrieve library rules using Retrieval-Augmented Generation (RAG).
- Calculate fines using a dedicated Python tool.
- Support follow-up questions using conversation context.
- Maintain member profile information.
- Stop safely when the required policy cannot be found.
- Route waiver requests through human approval.

## 2. System Architecture

```text
                     User Query
                         |
                         v
                    Supervisor
                         |
                         v
                    Policy Agent
                         |
                         v
                  RAG Policy Retriever
                         |
                         v
                 Relevant Policy Rules
                         |
                         v
                   Calculator Agent
                         |
                         v
                calculate_library_fine
                         |
                         v
                     Supervisor
                         |
                  +------+------+
                  |             |
                  v             v
              Final Answer   Human Approval
                              (If Required)
```

The supervisor coordinates the workflow and limits routing using `MAX_HOPS = 6`.

**Core design principle:** policy retrieval determines the applicable rules, while the calculator performs arithmetic. If no matching policy is retrieved, the system should stop rather than invent a rate.

## 3. Unit 3 — Memory and Retrieval-Augmented Generation

### 3.1 Conversation Memory

The system uses SQLite-backed thread memory to support follow-up questions and preserve relevant conversation context.

Example:

1. User: `A novel was returned 5 days late.`
2. User: `And if it were a reference book?`

The second question can use the previous conversation context rather than requiring the user to repeat the entire request.

### 3.2 Member Profile Storage

Member profile information is conceptually organized using a `profiles` table keyed by `member_id`.

This allows member-related information to be associated with the correct member.

### 3.3 Retrieval-Augmented Generation (RAG)

The policy document is stored at:

`ta2/docs/library_rules.txt`

The RAG retriever searches this document for relevant library rules, such as loan periods, daily fine rates, and waiver conditions.

The retrieved policy provides the information needed by the Policy Agent. Unsupported rules should not be fabricated.

### 3.4 SQLite Storage

The TA2 application uses a local SQLite database:

`ta2/library_ta2.db`

The database is generated or used locally by the application and is excluded from the Git repository.

## 4. Unit 4 — Multi-Agent Workflow

### Policy Agent

- Retrieves relevant policy information through RAG.
- Identifies applicable rules from the policy document.
- Does not perform fine calculations.
- Does not invent missing policy rates.

### Calculator Agent

- Uses the `calculate_library_fine` tool.
- Performs arithmetic using the applicable policy rate.
- Validates inputs, including negative late-day values.
- Reports calculation errors instead of treating them as valid fines.

### Supervisor Agent

- Coordinates the agents.
- Routes requests through the policy and calculator stages.
- Enforces the configured `MAX_HOPS = 6` limit.
- Stops processing when the required policy cannot be retrieved.

### Human Approval

Waiver requests require human approval rather than being granted automatically.

This adds a human-in-the-loop decision point to the workflow.

## 5. Technology Stack

- **Language:** Python
- **Agent orchestration:** LangGraph
- **Language model integration:** LangChain and Ollama
- **Local language model:** Qwen 2.5 3B
- **Retrieval-Augmented Generation:** Policy document retrieval
- **Database:** SQLite
- **Dependency management:** `requirements.txt`

## 6. Project Structure

```text
Library_Fine_Agent_RAG_MultiAgent/
│
├── README.md
├── .gitignore
├── requirements.txt
├── library_fine_agent.py
├── TA2_EVIDENCE.md
│
├── ta1/
│   └── library_fine_agent.py
│
└── ta2/
    ├── __init__.py
    ├── calculator_agent.py
    ├── evaluate_ta1_vs_ta2.py
    ├── human_approval.py
    ├── memory_agent.py
    ├── policy_agent.py
    ├── profile_store.py
    ├── rag_policy.py
    ├── run_ta2.py
    ├── supervisor.py
    │
    └── docs/
        └── library_rules.txt
```

The local SQLite database and temporary files are not included in this repository.

## 7. Installation and Execution

### Prerequisites

- Python installed and available from the command line.
- Git.
- Ollama installed and running.
- The Qwen 2.5 3B model downloaded through Ollama.

### Step 1: Clone the repository

```bash
git clone https://github.com/yashkalbhor1300/library-fine-agent.git
cd library-fine-agent
```

### Step 2: Create a virtual environment

Windows:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 4: Download the model

```bash
ollama pull qwen2.5:3b
```

Ensure Ollama is running and the model is available locally.

### Step 5: Run the TA2 application

From the project root:

```bash
python -m ta2.run_ta2
```

Follow the application's prompts to enter library-related queries.

## 8. Test Cases

Try the following inputs when running the application.

| Test case | Input | Expected behavior |
|---|---|---|
| Novel fine | `A novel was returned 5 days late.` | Retrieve the applicable rule and calculate the fine |
| Follow-up question | `And if it were a reference book?` | Reuse relevant conversation context |
| Negative late days | `Calculate the fine for a novel returned -3 days late.` | Return a clear validation error |
| Missing policy | `What is the laptop borrowing fee?` | Stop if no matching policy is retrieved |
| Waiver request | `A novel is 5 days late. Please waive the fine.` | Route the request through human approval |

### Expected Results

**Novel returned 5 days late**

Under the configured example policy rate of ₹2 per day:

`Fine = 5 × ₹2 = ₹10`

Expected result: **₹10**

**Missing policy**

Expected safe response:

> I could not find a matching rule in the library policy document, so I will not invent one.

The calculator should not be given an invented rate.

**Negative late days**

The calculator should return a validation error rather than a normal fine amount.

**Waiver request**

The request should be routed through the human-approval workflow. A waiver should not be granted automatically.

*Note: Expected results depend on the rules in `ta2/docs/library_rules.txt` and the application's implemented behavior.*

## 9. TA1 vs. TA2 Comparison

| Capability | TA1 Baseline | TA2 Extension |
|---|---|---|
| Fine calculation | Basic tool-based calculation | Policy retrieval followed by tool-based calculation |
| Policy retrieval | No RAG policy layer | Retrieves rules from the policy document |
| Follow-up questions | Limited context across fresh calls | Thread memory supports contextual follow-ups |
| Invalid inputs | Calculator validation | Validation with supervisor-coordinated handling |
| Missing policy | No dedicated RAG missing-policy check | Stops when no matching policy is found |
| Waiver requests | No human-approval gate | Human approval workflow |

## 10. Conceptual Routing Flow

A successful request follows this conceptual workflow:

```text
USER
  |
  v
SUPERVISOR
  |
  v
POLICY AGENT
  |
  v
RAG RETRIEVER
  |
  v
CALCULATOR AGENT
  |
  v
CALCULATION TOOL
  |
  v
SUPERVISOR
  |
  v
FINAL ANSWER
```

If the required policy cannot be found, the supervisor should stop the workflow instead of passing an invented rate to the calculator.

This diagram describes the intended agent-routing sequence; it is not a claim that a separate detailed execution-trace viewer has been implemented.

## 11. Important Design Decisions

**Why use RAG?**

RAG retrieves the relevant library rules from a policy document, helping ground the answer in the available source rather than relying only on the language model's internal knowledge.

**Why use a calculator tool?**

Arithmetic is performed by deterministic Python code, reducing the risk of incorrect calculations generated by a language model.

**Why use a supervisor?**

The supervisor coordinates the agents, controls the routing process, and prevents the workflow from continuing indefinitely.

**Why include human approval?**

Waiver requests require an explicit human decision rather than allowing the agent to approve its own exception.

**Why handle missing policy explicitly?**

When a policy cannot be found, stopping safely is preferable to inventing a borrowing fee or fine rate.

## 12. Conclusion

The Library Fine Agent demonstrates an agentic workflow that combines policy retrieval, tool-based calculation, conversation memory, profile storage, and human approval.

The project illustrates key concepts from Agentic AI Units 3 and 4, including multi-agent orchestration, RAG, tool use, stateful conversations, validation, and human-in-the-loop decision-making.

---

**Project:** Library Fine Agent — TA2  
**Subject:** Agentic AI  
**Repository:** https://github.com/yashkalbhor1300/library-fine-agent
