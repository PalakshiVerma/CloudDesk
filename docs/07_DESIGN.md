# CloudDesk — UI/UX Design System & Interface Wireframes

**Document Version:** 1.0.0  
**Project:** CloudDesk — AI-Assisted Support Ticket Triage & Routing Platform  
**Target Frontend:** Streamlit (Python Data App Framework) with Custom Modern CSS  
**Design Persona:** Modern Enterprise SaaS / Clean Dark & Light Hybrid Operations Console  
**Status:** Approved for Implementation  

---

## 1. Design Philosophy & Aesthetic Identity

CloudDesk is an operational command center built for high-tempo support environments. Its interface design prioritizes:
1. **Zero Cognitive Overhead:** High-volume queues require immediate visual hierarchy. Agents must distinguish critical issues, AI confidence levels, and department tags within 200 milliseconds of scanning a screen.
2. **Explainable AI First:** AI is never a "black box" in CloudDesk. Every machine prediction surfaces its confidence score, its concise explanation, and the exact knowledge sources used for grounding.
3. **Frictionless Human-in-the-Loop Actions:** Reviewing a low-confidence ticket must take fewer than 3 clicks: 1 click to inspect, 1 click to confirm or adjust, and 1 click to dispatch.

---

## 2. Design System Tokens & Color Palette

### 2.1 Color Palette

```text
SURFACE & BACKGROUND:
  Base Canvas:       #0F172A (Deep Slate Navy)
  Card Surface:      #1E293B (Midnight Slate)
  Border & Divider:  #334155 (Subtle Slate Border)
  Input Surface:     #0F172A (Inset Dark)

TYPOGRAPHY & ACCENTS:
  Primary Text:      #F8FAFC (Clean High-Contrast White)
  Secondary Text:    #94A3B8 (Muted Slate Gray)
  Brand Primary:     #6366F1 (Electric Indigo)
  Brand Hover:       #4F46E5 (Deep Indigo)

STATUS & FUNCTIONAL COLORS:
  Success (Auto-Route):  #10B981 (Emerald Green)
  Warning (Needs Review):#F59E0B (Amber Gold)
  Danger (Critical Sev): #EF4444 (Crimson Red)
  Info (In Progress):    #06B6D4 (Vibrant Cyan)
```

### 2.2 Status Badges & Priority Tokens

| Status / Priority | Background | Text Color | Visual Meaning |
| :--- | :--- | :--- | :--- |
| `auto_routed` | `rgba(16, 185, 129, 0.15)` | `#10B981` | Machine high confidence; successfully routed |
| `needs_review` | `rgba(245, 158, 11, 0.15)` | `#F59E0B` | Machine uncertain ($< 0.85$); requires human sign-off |
| `reviewed` | `rgba(6, 182, 212, 0.15)` | `#06B6D4` | Human agent verified or corrected |
| `pending_triage`| `rgba(148, 163, 184, 0.15)`| `#94A3B8` | In queue waiting for AI pipeline |
| `Critical (P1)` | `rgba(239, 68, 68, 0.2)` | `#EF4444` | Outage / Major security threat (Pulsing badge) |
| `High (P2)` | `rgba(249, 115, 22, 0.2)` | `#F97316` | Broken feature / Payment risk |
| `Medium (P3)` | `rgba(59, 130, 246, 0.2)` | `#3B82F6` | Standard defect with workaround |
| `Low (P4)` | `rgba(100, 116, 139, 0.2)`| `#94A3B8` | Minor query / Feature suggestion |

### 2.3 Confidence Meter Gradient
* **$\ge 0.85$ (High Certainty):** Green chip (`#10B981`) with label `94% Confidence (Auto-Eligible)`.
* **$0.70 - 0.84$ (Moderate Ambiguity):** Yellow chip (`#F59E0B`) with label `76% Confidence (Review Required)`.
* **$< 0.70$ (Low Certainty / Edge Case):** Red chip (`#EF4444`) with label `58% Confidence (High Human Scrutiny)`.

---

## 3. Global Navigation & Sidebar Layout

The Streamlit sidebar provides persistent context and status counts across pages:

```text
+-----------------------------------------------------------+
| [⚡ CloudDesk Operations Console]                          |
| User: Sarah Smith (AGENT) | Role: Tier-1 Specialist        |
+-----------------------------------------------------------+
| NAVIGATION:                                               |
|   📊 1. Operations Dashboard                              |
|   🎫 2. Ticket Explorer                                   |
|   👀 3. Review Queue (🔴 3 Pending)                       |
|   📚 4. Knowledge Base (RAG)                              |
|   🧪 5. Evaluation Studio (100-Set)                       |
|   ⚙️ 6. System Settings                                   |
+-----------------------------------------------------------+
| SYSTEM HEALTH:                                            |
|   ● FastAPI Backend:  CONNECTED (12ms)                    |
|   ● OpenAI Engine:    ONLINE (gpt-4o-mini)                |
|   ● Qdrant Vector:    HEALTHY (1,420 vectors)             |
|   ● Active Threshold: θ = 0.85                            |
+-----------------------------------------------------------+
```

---

## 4. Screen Wireframes & Component Layouts

### 4.1 Screen 1: Operations Dashboard (`1_Dashboard.py`)
Executive overview displaying real-time automation throughput, misroute reduction, and urgent alerts.

```text
+---------------------------------------------------------------------------------------------------+
| ⚡ CLOUDDESK OPERATIONS DASHBOARD                                          [Refresh] [Live Toggle]|
+---------------------------------------------------------------------------------------------------+
| ⚠️ CRITICAL ALERT BANNER: 2 Sev-1 Tickets Detected in last 30 mins (Security & Payment)            |
+---------------------------------------------------------------------------------------------------+
| [ TOTAL INGESTED ]   [ AUTO-ROUTED % ]   [ HUMAN ESCALATION ]   [ AVG TRIAGE TIME ] [ CRITICALS ] |
|       420                  82.8%                17.2%                 1.42s               14      |
|  ▲ +18% vs yesterday  Target: >80% (PASS)  Target: <20% (PASS)   Target: <10s (PASS)  P1 Queue    |
+---------------------------------------------------------------------------------------------------+
| 24-HOUR TRIAGE THROUGHPUT & AUTOMATION RATIO                      CATEGORY DISTRIBUTION DONUT    |
|                                                                                                   |
| Tickets                                                           [ Technical:  33% ■■■■■■■■    ] |
| 50 |      ╭───╮        Auto-routed (Green Area)                   [ Billing:    20% ■■■■■       ] |
| 40 |     ╭╯   ╰╮                                                  [ Payment:    16% ■■■■        ] |
| 30 |    ╭╯     ╰╮   ╭─╮                                           [ Account:    13% ■■■         ] |
| 20 |   ╭╯       ╰───╯ ╰╮ Human Escalated (Amber Line)             [ Integration:10% ■■          ] |
| 10 |───╯               ╰───                                       [ Security:    5% ■           ] |
|  0 +-----------------------                                       [ General:     3% ■           ] |
|    00:00  06:00  12:00  18:00                                                                     |
+---------------------------------------------------------------------------------------------------+
```

---

### 4.2 Screen 2: Ticket Explorer & Deep Inspector (`2_Tickets.py`)
Searchable, filterable inventory of all support tickets with side-drawer inspection.

```text
+---------------------------------------------------------------------------------------------------+
| 🎫 TICKET EXPLORER                                                                                |
| Search: [ "payment failed"                      ] Status: [ All ▼ ] Category: [ All ▼ ] [Apply]   |
+---------------------------------------------------------------------------------------------------+
| ID       | SUBJECT                           | CATEGORY | PRIORITY | TEAM         | CONF  | STATUS|
|----------+-----------------------------------+----------+----------+--------------+-------+-------|
| #1042    | Payment deducted twice on Pro...  | Payment  | High     | Billing & Fin| 94%   | [AUTO]|
| #1043    | Intermittent webhook delivery...  | Technical| Medium   | (Pending)    | 68%   | [REVW]|
| #1044    | SAML SSO cert renewal lockout...  | Security | Critical | Security     | 96%   | [AUTO]|
| #1045    | How do I invite team members?...  | General  | Low      | Tier 1 Supp  | 98%   | [AUTO]|
+---------------------------------------------------------------------------------------------------+
| SELECTED TICKET DETAIL (#1043):                                                                   |
| Subject: Intermittent webhook delivery failures during peak hours                                 |
| Customer: devops@techstart.io | Created: 11:40 UTC | Source: Webhook                             |
| Description: "Our developers noticed that between 14:00 and 15:00 UTC, webhooks to our endpoint   |
| failed with timeout. We also had a minor invoice credit question."                                |
|                                                                                                   |
| [ AI TRIAGE INSPECTION ]                                                                          |
| Category: Technical (68%) | Priority: Medium | Team: Technical Support                           |
| Reasoning: "Mentions both webhook timeouts and invoice question. Confidence 0.68 is below 0.85."  |
| Grounding Context: Retrieved Runbook: 'Webhook Retries & Failure Codes' (Score: 0.84)             |
|                                                                                                   |
| [ AUDIT TIMELINE ]                                                                                |
| 11:40:02 - Ingested via Mock Webhook                                                              |
| 11:40:03 - AI Evaluated (Latency: 1.1s) -> Diverted to Review Queue (Confidence 0.68 < 0.85)       |
+---------------------------------------------------------------------------------------------------+
```

---

### 4.3 Screen 3: Human Review Queue (`3_Review_Queue.py`)
Optimized workstation allowing agents to triage uncertain tickets with maximum speed.

```text
+---------------------------------------------------------------------------------------------------+
| 👀 HUMAN REVIEW QUEUE (🔴 3 Tickets Require Attention)                      [Review Mode: Active]  |
+---------------------------------------------------------------------------------------------------+
| REVIEW ITEM 1 OF 3: Ticket #1043                                                                  |
+---------------------------------------------------+-----------------------------------------------+
| 📄 INBOUND CUSTOMER CONTEXT                       | 🤖 AI PREDICTION & REASONING                  |
| Subject: Intermittent webhook delivery failures   | Predicted Category: Technical                 |
| Customer: devops@techstart.io                     | Suggested Team:     Technical Support         |
| Organization: TechStart Solutions (Enterprise)    | Confidence:         68% (AMBIGUOUS - BELOW θ) |
| Description:                                      | Assessed Priority:  Medium                    |
| "Our developers noticed that between 14:00 and    |                                               |
| 15:00 UTC, webhooks to our endpoint failed with   | AI Explanation:                               |
| timeout. We also had an invoice credit question." | "Issue spans webhook errors and billing;      |
|                                                   | needs human clarification."                   |
+---------------------------------------------------+-----------------------------------------------+
| ACTION STATION:                                                                                   |
|                                                                                                   |
| [ ✔️ APPROVE AI RECOMMENDATION ] (Assign to Technical Support as Medium Priority)                 |
|                                                                                                   |
| --- OR CORRECT / OVERRIDE ---                                                                     |
| Correct Category: [ Integration ▼ ]  Correct Team: [ Integrations Team ▼ ] Priority: [ High ▼ ]   |
| Override Reason:  [ Core issue is webhook failure; customer revenue is blocked.                 ] |
| [ 🔄 SUBMIT CORRECTION & ROUTE ]                                                                  |
+---------------------------------------------------------------------------------------------------+
```

---

### 4.4 Screen 4: Evaluation Studio (`5_Evaluation.py`)
Demonstrable evaluation bench verifying KPIs against the 100-ticket ground truth set.

```text
+---------------------------------------------------------------------------------------------------+
| 🧪 EVALUATION & BENCHMARK STUDIO                                                                  |
| Ground Truth Dataset: evaluation_set.json (100 Labeled Tickets)                                   |
| [ ▶️ RUN BENCHMARK EVALUATION (100 TICKETS) ]                                                      |
+---------------------------------------------------------------------------------------------------+
| BENCHMARK SCORECARD:                                                                              |
| [ CLASSIFICATION ACCURACY ]  [ ROUTING ACCURACY ]  [ CRITICAL RECALL ]  [ ESCALATION RATE ]       |
|            89.0%                    88.0%                  94.1%                 16.0%            |
|       (Target: >85% PASS)      (Target: >85% PASS)    (Target: >90% PASS)   (Target: <20% PASS)   |
+---------------------------------------------------------------------------------------------------+
| 7x7 CATEGORY CONFUSION MATRIX (Rows: Actual, Columns: Predicted)                                  |
|               Acc   Bill   Paym   Tech   Secu   Inte   Gene                                       |
| Account    |  14      0      0      1      0      0      0   | 93.3% Accuracy                       |
| Billing    |   0     18      2      0      0      0      0   | 90.0% Accuracy                       |
| Payment    |   0      1     15      0      0      0      0   | 93.8% Accuracy                       |
| Technical  |   1      0      0     22      0      2      0   | 88.0% Accuracy                       |
| Security   |   0      0      0      0      9      1      0   | 90.0% Accuracy                       |
| Integration|   0      0      0      2      0     10      0   | 83.3% Accuracy                       |
| General    |   0      1      0      0      0      0      9   | 90.0% Accuracy                       |
+---------------------------------------------------------------------------------------------------+
| MISCLASSIFICATION ERROR LOG (Drill-Down on 11 Errors):                                            |
| Ticket #34: Actual 'Integration' predicted as 'Technical' (Confidence: 0.62 -> Escapement Caught)|
+---------------------------------------------------------------------------------------------------+
```
