# CloudDesk — REST API Specification

**Document Version:** 1.0.0  
**Project:** CloudDesk — AI-Assisted Support Ticket Triage & Routing Platform  
**Base URL:** `http://localhost:8000/api/v1`  
**OpenAPI / Swagger Spec:** Interactive docs available at `/docs` (Swagger UI) and `/redoc` (ReDoc).  
**Status:** Approved for Implementation  

---

## 1. Global Standards & Conventions

### 1.1 Headers
* `Content-Type`: `application/json`
* `Authorization`: `Bearer <jwt_token>` (Required for all endpoints except `/auth/login` and `/webhooks/*`).

### 1.2 Standard Error Response Schema
All error responses adhere to the RFC 7807 Problem Details structure:
```json
{
  "detail": {
    "error_code": "TICKET_NOT_FOUND",
    "message": "Ticket with ID '550e8400-e29b-41d4-a716-446655440000' does not exist.",
    "context": { "ticket_id": "550e8400-e29b-41d4-a716-446655440000" }
  }
}
```

### 1.3 Common HTTP Status Codes
* `200 OK`: Request succeeded; entity returned.
* `201 Created`: Entity successfully created.
* `204 No Content`: Action succeeded; no body returned.
* `400 Bad Request`: Business rule validation error.
* `401 Unauthorized`: Missing or expired JWT token.
* `403 Forbidden`: Insufficient RBAC privileges.
* `404 Not Found`: Resource does not exist.
* `422 Unprocessable Entity`: Request body violates Pydantic schema.
* `500 Internal Server Error`: Unhandled server exception.

---

## 2. Authentication Endpoints

### 2.1 Login & Obtain JWT Token
* **Endpoint:** `POST /api/v1/auth/login`
* **Access:** Public
* **Request Body:**
```json
{
  "email": "agent.smith@clouddesk.internal",
  "password": "Password123!"
}
```
* **Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "7fa8b210-911e-45de-8219-90b4112e0001",
    "email": "agent.smith@clouddesk.internal",
    "full_name": "Sarah Smith",
    "role": "AGENT"
  }
}
```

### 2.2 Get Current User Profile
* **Endpoint:** `GET /api/v1/auth/me`
* **Access:** Authenticated (`AGENT`, `TEAM_LEAD`, `ADMIN`)
* **Response (200 OK):**
```json
{
  "id": "7fa8b210-911e-45de-8219-90b4112e0001",
  "email": "agent.smith@clouddesk.internal",
  "full_name": "Sarah Smith",
  "role": "AGENT",
  "is_active": true
}
```

---

## 3. Ticket Management Endpoints

### 3.1 Create Ticket & Trigger Automatic Triage
* **Endpoint:** `POST /api/v1/tickets`
* **Access:** Authenticated or API Key
* **Request Body:**
```json
{
  "subject": "Payment deducted twice but account is still on free plan",
  "description": "I upgraded to Pro annual plan today at 09:15 UTC. My credit card statement shows two charges of $240 each, but my workspace still says Free Plan. Please fix and refund the duplicate charge immediately.",
  "customer_email": "finance@acmecorp.com",
  "customer_name": "John Doe",
  "source": "portal"
}
```
* **Response (201 Created):**
```json
{
  "id": "b3e944d1-c124-4f81-995b-38d73bdf6721",
  "external_id": null,
  "subject": "Payment deducted twice but account is still on free plan",
  "status": "auto_routed",
  "priority": "High",
  "category": "Payment",
  "assigned_team": {
    "id": "11111111-2222-3333-4444-555555555552",
    "name": "Billing & Finance",
    "slug": "billing-finance"
  },
  "prediction": {
    "predicted_category": "Payment",
    "predicted_priority": "High",
    "confidence": 0.940,
    "reason": "Customer was charged twice for an annual subscription upgrade but workspace remains on free tier. Requires financial reconciliation.",
    "is_auto_routed": true,
    "latency_ms": 1180
  },
  "created_at": "2026-09-28T11:45:00.123Z"
}
```

### 3.2 List Tickets
* **Endpoint:** `GET /api/v1/tickets`
* **Query Parameters:**
  * `status` (string, optional): e.g., `pending_triage`, `auto_routed`, `needs_review`, `resolved`.
  * `category` (string, optional): e.g., `Payment`, `Technical`.
  * `priority` (string, optional): `Low`, `Medium`, `High`, `Critical`.
  * `team_id` (UUID, optional): Filter by assigned team.
  * `page` (int, default: 1): Page number.
  * `page_size` (int, default: 20): Items per page.
* **Response (200 OK):**
```json
{
  "items": [
    {
      "id": "b3e944d1-c124-4f81-995b-38d73bdf6721",
      "subject": "Payment deducted twice but account is still on free plan",
      "status": "auto_routed",
      "priority": "High",
      "category": "Payment",
      "team_name": "Billing & Finance",
      "confidence": 0.940,
      "created_at": "2026-09-28T11:45:00.123Z"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

### 3.3 Get Ticket Details
* **Endpoint:** `GET /api/v1/tickets/{id}`
* **Response (200 OK):**
```json
{
  "id": "b3e944d1-c124-4f81-995b-38d73bdf6721",
  "external_id": null,
  "subject": "Payment deducted twice but account is still on free plan",
  "description": "I upgraded to Pro annual plan today at 09:15 UTC...",
  "customer_email": "finance@acmecorp.com",
  "customer_name": "John Doe",
  "status": "auto_routed",
  "priority": "High",
  "category": "Payment",
  "assigned_team": {
    "id": "11111111-2222-3333-4444-555555555552",
    "name": "Billing & Finance"
  },
  "prediction": {
    "id": "a9101112-bbbb-cccc-dddd-eeeeeeeeeeee",
    "predicted_category": "Payment",
    "predicted_priority": "High",
    "confidence": 0.940,
    "reason": "Customer was charged twice for an annual subscription upgrade...",
    "suggested_resolution": "Verify Stripe event invoices, issue refund for duplicate transaction, and manually upgrade workspace entitlement.",
    "model_name": "gpt-4o-mini",
    "latency_ms": 1180,
    "is_auto_routed": true
  },
  "reviews": [],
  "audit_trail": [
    {
      "event_type": "TICKET_CREATED",
      "created_at": "2026-09-28T11:45:00.123Z"
    },
    {
      "event_type": "AUTO_ROUTED",
      "created_at": "2026-09-28T11:45:01.303Z",
      "metadata": { "confidence": 0.940, "team": "Billing & Finance" }
    }
  ]
}
```

---

## 4. Human Review & Override Endpoints

### 4.1 Fetch Review Queue
* **Endpoint:** `GET /api/v1/reviews/queue`
* **Query Parameters:** `page`, `page_size`
* **Response (200 OK):**
```json
{
  "queue_length": 3,
  "items": [
    {
      "ticket_id": "c4d871e2-a312-4012-8822-123456789abc",
      "subject": "Intermittent webhook delivery failures during peak hours",
      "description": "Our developers noticed that between 14:00 and 15:00 UTC, webhooks to our endpoint failed with timeout. We also had an invoice question.",
      "customer_email": "devops@techstart.io",
      "created_at": "2026-09-28T11:40:00Z",
      "suggested_category": "Technical",
      "suggested_priority": "Medium",
      "suggested_team": "Technical Support",
      "confidence": 0.680,
      "reason": "Contains mixed intent regarding webhook failures and billing inquiry; confidence below 0.85 threshold."
    }
  ]
}
```

### 4.2 Approve AI Decision
* **Endpoint:** `POST /api/v1/reviews/{ticket_id}/approve`
* **Access:** Authenticated (`AGENT`, `TEAM_LEAD`, `ADMIN`)
* **Request Body:** `{}` (Empty JSON)
* **Response (200 OK):**
```json
{
  "ticket_id": "c4d871e2-a312-4012-8822-123456789abc",
  "status": "reviewed",
  "assigned_team": "Technical Support",
  "action": "approved",
  "message": "AI recommendation confirmed by agent."
}
```

### 4.3 Override / Correct AI Decision
* **Endpoint:** `POST /api/v1/reviews/{ticket_id}/correct`
* **Access:** Authenticated (`AGENT`, `TEAM_LEAD`, `ADMIN`)
* **Request Body:**
```json
{
  "corrected_category": "Integration",
  "corrected_priority": "High",
  "corrected_team_id": "11111111-2222-3333-4444-555555555555",
  "override_reason": "Primary issue is third-party webhook delivery failure causing data loss, belongs with Integrations team."
}
```
* **Response (200 OK):**
```json
{
  "ticket_id": "c4d871e2-a312-4012-8822-123456789abc",
  "status": "reviewed",
  "assigned_team": "Integrations Team",
  "action": "overridden",
  "delta": {
    "category": { "from": "Technical", "to": "Integration" },
    "team": { "from": "Technical Support", "to": "Integrations Team" }
  },
  "message": "Ticket successfully corrected and dispatched."
}
```

---

## 5. Knowledge Base & RAG Endpoints

### 5.1 Ingest Knowledge Document
* **Endpoint:** `POST /api/v1/knowledge/upload`
* **Access:** `ADMIN`, `TEAM_LEAD`
* **Request Body:**
```json
{
  "title": "Stripe Webhook & Payment Reconciliation Protocol",
  "category": "Payment",
  "content": "# Stripe Payment Troubleshooting\nWhen a payment succeeds in Stripe but workspace is inactive..."
}
```
* **Response (201 Created):**
```json
{
  "id": "e817291a-1234-5678-9abc-def012345678",
  "title": "Stripe Webhook & Payment Reconciliation Protocol",
  "chunks_created": 3,
  "vectors_upserted": 3,
  "status": "indexed"
}
```

### 5.2 Semantic Search Query
* **Endpoint:** `POST /api/v1/knowledge/search`
* **Request Body:**
```json
{
  "query": "card charged but account not upgraded",
  "limit": 3
}
```
* **Response (200 OK):**
```json
{
  "results": [
    {
      "title": "Stripe Webhook & Payment Reconciliation Protocol",
      "score": 0.892,
      "snippet": "When a payment succeeds in Stripe but workspace is inactive, verify Stripe event invoice.payment_succeeded..."
    }
  ]
}
```

---

## 6. Dashboard & Analytics Endpoints

### 6.1 Get Operations KPIs
* **Endpoint:** `GET /api/v1/dashboard/stats`
* **Response (200 OK):**
```json
{
  "total_tickets": 420,
  "auto_routed_count": 348,
  "auto_routed_percentage": 82.86,
  "human_reviewed_count": 72,
  "human_reviewed_percentage": 17.14,
  "avg_triage_time_seconds": 1.42,
  "critical_urgent_count": 14,
  "review_queue_pending": 3
}
```

### 6.2 Category Distribution Breakdown
* **Endpoint:** `GET /api/v1/dashboard/categories`
* **Response (200 OK):**
```json
{
  "categories": [
    { "name": "Technical", "count": 140, "percentage": 33.3 },
    { "name": "Billing", "count": 85, "percentage": 20.2 },
    { "name": "Payment", "count": 65, "percentage": 15.5 },
    { "name": "Account", "count": 55, "percentage": 13.1 },
    { "name": "Integration", "count": 40, "percentage": 9.5 },
    { "name": "Security", "count": 20, "percentage": 4.8 },
    { "name": "General", "count": 15, "percentage": 3.6 }
  ]
}
```

---

## 7. Evaluation & Benchmark Endpoints

### 7.1 Run 100-Ticket Benchmark Evaluation
* **Endpoint:** `POST /api/v1/evaluation/run`
* **Access:** `ADMIN`
* **Response (200 OK):**
```json
{
  "run_id": "99887766-5544-3322-1100-aabbccddeeff",
  "total_tickets": 100,
  "classification_accuracy": 89.0,
  "routing_accuracy": 88.0,
  "critical_recall": 94.1,
  "human_escalation_rate": 16.0,
  "avg_latency_ms": 1120,
  "kpi_status": {
    "classification_accuracy_passed": true,
    "routing_accuracy_passed": true,
    "critical_recall_passed": true,
    "human_escalation_passed": true
  }
}
```

---

## 8. Mock External Helpdesk Webhooks

### 8.1 Inbound Helpdesk Webhook
* **Endpoint:** `POST /api/v1/webhooks/mock-helpdesk/tickets`
* **Request Body:**
```json
{
  "external_id": "ZD-89412",
  "subject": "Cannot log in with SSO after SAML cert update",
  "description": "Our company Okta SAML cert expired and was renewed, now all 50 employees get 401 Unauthorized when logging in.",
  "customer_email": "admin@enterprise.org",
  "created_at": "2026-09-28T11:30:00Z"
}
```
* **Response (200 OK):**
```json
{
  "status": "received_and_triaged",
  "clouddesk_id": "f5e4d3c2-b1a0-9876-5432-10fedcba9876",
  "assigned_team": "Security & Compliance",
  "priority": "Critical",
  "confidence": 0.960
}
```

### 8.2 Outbound Callback Simulator (Listener)
* **Endpoint:** `POST /api/v1/webhooks/mock-helpdesk/status-update`
* **Description:** Receives callbacks sent by CloudDesk's routing engine when tickets are updated or routed.
