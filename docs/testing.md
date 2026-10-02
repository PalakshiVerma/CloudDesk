# CloudDesk — Comprehensive Testing Strategy & Evaluation Plan

**Document Version:** 1.0.0  
**Project:** CloudDesk — AI-Assisted Support Ticket Triage & Routing Platform  
**Testing Frameworks:** Pytest 8.0+, HTTPX (AsyncClient), Coverage.py  
**Status:** Mandatory Testing Policy  

---

## 1. Multi-Tier Testing Pyramid

CloudDesk applies a four-tiered verification framework to guarantee both traditional software reliability and AI probabilistic safety.

```text
               ▲
              / \
             /E2E\             Tier 4: End-to-End Workflow Verification
            /-----\            (Ingestion -> Triage -> Review -> Audit)
           / Inte- \
          / gration \          Tier 3: API & Transaction Integration Tests
         /-----------\         (FastAPI + PostgreSQL + Webhooks)
        / AI & Model  \
       /  Evaluation   \       Tier 2: 100-Ticket Labeled Ground Truth Benchmark
      /-----------------\      (Accuracy, Recall, Confusion Matrix)
     /    Unit Tests     \
    / (Schemas & Service) \    Tier 1: Fast Deterministic Pytest Suites
   /-----------------------\   (Pydantic, Threshold Logic, State Transitions)
```

---

## 2. Test Suites & Coverage Requirements

### 2.1 Tier 1: Unit Testing (Fast, Isolated, Mocked)
* **Target Files:** `tests/test_routing_engine.py`, `tests/test_pydantic_schemas.py`
* **Coverage Objective:** $> 85\%$ on all domain services.
* **Key Unit Scenarios:**
  * Validate that confidence scores $\ge 0.85$ deterministically return `AUTO_ROUTE`.
  * Validate that confidence scores $< 0.85$ deterministically return `HUMAN_REVIEW`.
  * Validate that confidence values $< 0.0$ or $> 1.0$ raise Pydantic `ValidationError`.
  * Validate that unsupported category strings (e.g., `"Sales"`) fail enum validation.
  * Validate ticket state machine transition guards (cannot transition from `closed` to `auto_routed`).

### 2.2 Tier 2: AI & LLM Evaluation Benchmark (100-Ticket Set)
* **Target File:** `tests/test_evaluation_benchmark.py`
* **Test Dataset:** `tests/data/evaluation_set.json` (100 hand-labeled B2B tickets across 7 categories and 4 priorities).
* **Target KPIs (Must Pass):**

| Metric | Target | Formula | Purpose |
| :--- | :--- | :--- | :--- |
| **Classification Accuracy** | **$> 85\%$** | $\frac{\text{Correct Category Predictions}}{100} \times 100$ | Measures core taxonomy understanding. |
| **Routing Accuracy** | **$> 85\%$** | $\frac{\text{Correct Team Assignments}}{100} \times 100$ | Measures departmental routing precision. |
| **Critical Urgent Recall** | **$> 90\%$** | $\frac{\text{Detected Critical Tickets}}{\text{Actual Critical Tickets in Set}} \times 100$ | Ensures outages are never downgraded or missed. |
| **Human Escalation Rate** | **$< 20\%$** | $\frac{\text{Tickets Sent to Review Queue}}{100} \times 100$ | Ensures agents are not flooded with manual triage. |
| **Invalid AI Output Rate** | **$< 2\%$** | $\frac{\text{Malformed Responses}}{100} \times 100$ | Validates Pydantic JSON mode reliability. |
| **Average Triage Latency**| **$< 10$ sec**| $\frac{\sum \text{Inference Latency}}{100}$ | Guarantees sub-second/real-time performance. |

### 2.3 Tier 3: API & Database Integration Testing
* **Target Files:** `tests/test_api_tickets.py`, `tests/test_human_review.py`, `tests/test_mock_webhook.py`
* **Key Scenarios:**
  * `POST /api/v1/tickets` creates a record in `tickets` and `ticket_predictions`.
  * `POST /api/v1/reviews/{id}/approve` transitions ticket to `reviewed` and writes `HUMAN_APPROVED` to `audit_logs`.
  * `POST /api/v1/reviews/{id}/correct` updates ticket category/team, inserts into `human_reviews`, and records `HUMAN_OVERRIDDEN` in `audit_logs`.
  * `POST /api/v1/webhooks/mock-helpdesk/tickets` simulates inbound webhook and triggers outbound callback.

### 2.4 Tier 4: Failure & Circuit-Breaker Testing
* **Target File:** `tests/test_failure_modes.py`
* **Key Scenarios:**
  * Simulate OpenAI API timeout ($> 8000$ms): verify ticket persists with `status = "needs_review"` and reason `"AI Service Offline"`.
  * Simulate OpenAI HTTP 429 Rate Limit: verify exponential backoff executes and falls back safely to review queue without crashing.
  * Simulate Qdrant offline: verify triage executes using baseline LLM prompt without RAG grounding.

---

## 3. Mock AI Fixtures for Deterministic CI/CD

To prevent burning API credits and eliminate network flakiness in automated testing pipelines, CloudDesk includes a deterministic Mock AI Provider:

```python
# tests/conftest.py
import pytest
from app.schemas.ai import AIPredictionOutput, TicketCategory, TicketPriority, RecommendedTeam

class MockAIService:
    async def triage_ticket(self, ticket_id, subject, description) -> AIPredictionOutput:
        text = (subject + " " + description).lower()
        if "charge" in text or "payment" in text or "stripe" in text:
            return AIPredictionOutput(
                category=TicketCategory.PAYMENT,
                priority=TicketPriority.HIGH,
                recommended_team=RecommendedTeam.BILLING_FINANCE,
                confidence=0.94,
                reason="Detected payment keywords in text.",
                suggested_resolution="Verify Stripe payment ID."
            )
        elif "sso" in text or "breach" in text or "security" in text:
            return AIPredictionOutput(
                category=TicketCategory.SECURITY,
                priority=TicketPriority.CRITICAL,
                recommended_team=RecommendedTeam.SECURITY_COMPLIANCE,
                confidence=0.96,
                reason="Detected security/SSO keywords in text.",
                suggested_resolution="Check identity provider logs."
            )
        else:
            return AIPredictionOutput(
                category=TicketCategory.GENERAL,
                priority=TicketPriority.LOW,
                recommended_team=RecommendedTeam.TIER_1_SUPPORT,
                confidence=0.72,  # Diverts to human review
                reason="Ambiguous general inquiry.",
                suggested_resolution="Review documentation."
            )

@pytest.fixture
def mock_ai_service():
    return MockAIService()
```

---

## 4. Test Execution Commands

### Run All Unit and Integration Tests:
```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Run Only Routing and Threshold Tests:
```bash
pytest tests/test_routing_engine.py -v
```

### Execute the 100-Ticket Ground Truth Benchmark Suite:
```bash
pytest tests/test_evaluation_benchmark.py -v -s
```

### Run With Live OpenAI API (Integration Validation):
```bash
pytest tests/test_evaluation_benchmark.py -v -s --use-live-ai
```
