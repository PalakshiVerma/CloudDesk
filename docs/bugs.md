# CloudDesk — Bug Tracking, Known Issues & Edge Cases Ledger

**Document Version:** 1.0.0  
**Project:** CloudDesk — AI-Assisted Support Ticket Triage & Routing Platform  
**Status:** Active Bug & Incident Registry  

---

## 1. Bug Report Template

When logging new bugs or operational incidents, use the following standardized structure:

```markdown
### [BUG-XXX] Short Descriptive Title
- **Severity:** [ Critical (P1) | High (P2) | Medium (P3) | Low (P4) ]
- **Component:** [ AI Engine | API Gateway | Routing Engine | Database | Frontend UI | Webhooks ]
- **Reported Date:** YYYY-MM-DD
- **Reported By:** [Name/Role]
- **Status:** [ Open | In Progress | Resolved | Closed | Won't Fix ]

#### 1. Description & Impact
Clear explanation of what broke and how it affects support operations or customers.

#### 2. Steps to Reproduce
1. Step one...
2. Step two...
3. Step three...

#### 3. Expected vs. Actual Behavior
- **Expected:** The system should...
- **Actual:** Instead, the system...

#### 4. Root Cause Analysis (RCA)
Technical explanation of underlying fault (e.g. unhandled null field, regex flaw, race condition).

#### 5. Resolution & Verification
Summary of code changes and test case added to prevent regression.
```

---

## 2. Tracked Known Issues & Architecture Edge Cases

### [BUG-001] LLM JSON Mode Truncation on Oversized Ticket Descriptions
- **Severity:** High (P2)
- **Component:** AI Engine (`ai_service.py`)
- **Status:** Mitigated / Defensive Rule Enforced
- **Description:** If a customer pastes a massive log file (e.g., 20,000 characters) into the ticket description, the combined prompt exceeds context or token limits, causing the model to output truncated, unparseable JSON.
- **Root Cause:** Lack of input character bounding before dispatching to LLM API.
- **Resolution:** Implemented pre-processing sanitization that truncates ticket descriptions to 3,000 characters with an ellipsis indicator before formulating the prompt.

---

### [BUG-002] Confidence Oscillation on Mixed-Intent Support Inquiries
- **Severity:** Medium (P3)
- **Component:** Routing Engine (`routing_service.py`)
- **Status:** Mitigated by Design
- **Description:** Tickets that span multiple departments (e.g., "Our webhook fails and also what is our annual invoice amount?") return borderline confidence scores between 0.82 and 0.86, sometimes erroneously passing threshold.
- **Root Cause:** LLM prompt ambiguity when multiple strong category keywords co-occur.
- **Resolution:** Added explicit system prompt instruction: *"If multiple conflicting intents are present, choose the most severe/urgent one and penalize your confidence score to reflect ambiguity."* Added few-shot exemplar in `08_AI_SPEC.md`.

---

### [BUG-003] Inbound Webhook Missing Required Customer Identity Fields
- **Severity:** Medium (P3)
- **Component:** Webhooks Gateway (`webhooks.py`)
- **Status:** Resolved
- **Description:** Some third-party helpdesk webhooks send anonymous or unauthenticated tickets where `customer_email` is `null`, triggering a Pydantic validation 422 error and dropping the ticket.
- **Root Cause:** Strict non-nullable constraint on `customer_email` in the API schema.
- **Resolution:** Allowed fallback default `customer_email: Optional[str] = "support-unassigned@external-helpdesk.com"` on webhook ingestion models.

---

### [BUG-004] Vector Dimension Mismatch Between Embedding Models
- **Severity:** High (P2)
- **Component:** Vector DB (`rag_service.py` / Qdrant)
- **Status:** Mitigated by Architecture
- **Description:** Switching between OpenAI (`text-embedding-3-small` - 1536d) and local Hugging Face (`all-MiniLM-L6-v2` - 384d) causes Qdrant point upsert rejections due to dimension mismatch.
- **Root Cause:** Fixed vector collection schema in Qdrant initialized with static dimension size.
- **Resolution:** Parameterized vector collection dimension in `config.py` (`EMBEDDING_DIMENSION = 1536`). Automated collection recreation script checks dimension compatibility on startup.

---

### [BUG-005] Database Connection Pool Starvation During 100-Ticket Batch Benchmark
- **Severity:** High (P2)
- **Component:** Persistence Layer (`database.py`)
- **Status:** Resolved
- **Description:** Running the 100-ticket evaluation benchmark with `asyncio.gather()` opens 100 concurrent database connections simultaneously, exceeding default PostgreSQL connection limits and failing with `TooManyConnectionsError`.
- **Root Cause:** Unbounded concurrency during batch test execution.
- **Resolution:** Applied `asyncio.Semaphore(10)` to restrict concurrent inference and database operations to 10 parallel workers during benchmark execution.

---

## 3. Bug Severity & SLA Triage Matrix

| Severity Tier | Definition | Response SLA | Target Resolution |
| :--- | :--- | :--- | :--- |
| **Critical (P1)** | Platform down; inbound tickets failing to persist; security breach. | Immediate (< 15m) | < 4 hours |
| **High (P2)** | AI triage failing for entire category; human review queue blocked. | < 1 hour | < 1 business day |
| **Medium (P3)** | Edge-case misclassification; cosmetic UI defect; minor latency increase. | < 4 hours | Next sprint cycle |
| **Low (P4)** | Documentation typos; minor logging formatting adjustments. | < 2 business days | Backlog |
