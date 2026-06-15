# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `A04`) are preserved.

## 1. Team Metadata
- GROUP_NAME: "A04"
- REPO_URL: https://github.com/haongocng/2A202600903-NguyenNgocHao-Day13/tree/main
- MEMBERS: Nguyễn Ngọc Hảo
  - Member A: [Name] | Role: Logging & PII
  - Member B: [Name] | Role: Tracing & Enrichment
  - Member C: [Name] | Role: SLO & Alerts
  - Member D: [Name] | Role: Load Test & Dashboard
  - Member E: [Name] | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- VALIDATE_LOGS_FINAL_SCORE: 100/100
- [TOTAL_TRACES_COUNT]: at least 20 traces verified in Langfuse UI/API
- PII_LEAKS_FOUND: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: Screenshot of load test output/logs showing `req-...` correlation IDs and final validation output.
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: Screenshot of logs/traces showing `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, and `[REDACTED_CREDIT_CARD]`.
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: Screenshot of Langfuse tracing views showing `agent-run` root observations and `fake-llm-generate` generation observations.
- [TRACE_WATERFALL_EXPLANATION]: Each `/chat` request creates a trace named `chat-request`. The root observation is `agent-run`, which captures request-level context such as hashed user ID, session ID, feature, model, latency, and quality score. The child generation `fake-llm-generate` captures prompt preview, output preview, model name, token usage, and cost. This hierarchy makes it possible to see the agent pipeline and isolate slow generation/RAG behavior.

Final validation output:

```text
--- Lab Verification Results ---
Total log records analyzed: 195
Records with missing required fields: 0
Records with missing enrichment (context): 0
Unique correlation IDs found: 92
Potential PII leaks detected: 0

--- Grading Scorecard (Estimates) ---
+ [PASSED] Basic JSON schema
+ [PASSED] Correlation ID propagation
+ [PASSED] Log enrichment
+ [PASSED] PII scrubbing

Estimated Score: 100/100
```

Langfuse trace evidence:

```text
Trace name: chat-request
Root observation: agent-run
Generation observation: fake-llm-generate
Model: claude-sonnet-4-5
Tags: lab, qa/summary, claude-sonnet-4-5
Example trace id: d57beff0d5bfd545fc9260610b6d7f32
```

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: Screenshot of `/dashboard` showing Latency, Traffic, Error Rate, Cost, Tokens, and Quality panels.
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 157ms normal / 2655ms during `rag_slow` |
| Error Rate | < 2% | 28d | 0% |
| Cost Budget | < $2.5/day | 1d | $0.0211 in final normal snapshot |

Final normal metrics snapshot:

```json
{
  "traffic": 10,
  "latency_p50": 153.0,
  "latency_p95": 157.0,
  "latency_p99": 157.0,
  "avg_cost_usd": 0.0021,
  "total_cost_usd": 0.0211,
  "tokens_in_total": 340,
  "tokens_out_total": 1341,
  "error_breakdown": {},
  "quality_avg": 0.88
}
```

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: Screenshot of `config/alert_rules.yaml` showing `high_latency_p95`, `high_error_rate`, and `cost_budget_spike`.

Configured high-latency alert:

```yaml
- name: high_latency_p95
  severity: P2
  condition: latency_p95_ms > 2500 for 5m
  type: symptom-based
  owner: team-oncall
  runbook: docs/alerts.md#1-high-latency-p95
```

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: `rag_slow`
- [SYMPTOMS_OBSERVED]: Client-side load test latency increased from roughly 150-800ms to 8.8-14.9s. Metrics endpoint showed `latency_p95` increasing to `2655ms`, while `error_breakdown` stayed `{}`.
- [ROOT_CAUSE_PROVED_BY]: Incident toggle output confirmed `{'rag_slow': True}`. Langfuse traces showed `chat-request` traces with `agent-run` root observations and `fake-llm-generate` generation observations during the slow period. Metrics after incident showed P95 latency above the configured `2500ms` alert threshold.
- [FIX_ACTION]: Disabled the incident with `python scripts\inject_incident.py --scenario rag_slow --disable`, returning incidents to `{'rag_slow': False, 'tool_fail': False, 'cost_spike': False}`.
- [PREVENTIVE_MEASURE]: Keep the `high_latency_p95` alert and runbook active, inspect slow traces by feature/model, compare RAG and LLM spans, add fallback retrieval or query truncation for slow RAG paths, and keep dashboard threshold lines visible.

Incident evidence:

```text
python scripts\inject_incident.py --scenario rag_slow
200 {'ok': True, 'incidents': {'rag_slow': True, 'tool_fail': False, 'cost_spike': False}}
```

```text
[200] req-b0541b5a | qa | 8884.8ms
[200] req-bb8b4f2a | qa | 8884.1ms
[200] req-8c975f03 | qa | 11836.0ms
[200] req-7753694e | summary | 14801.5ms
[200] req-b0fa3cda | qa | 14804.9ms
[200] req-3d49ebc9 | qa | 14838.0ms
[200] req-875d0510 | summary | 14839.8ms
[200] req-5590f668 | qa | 11887.3ms
[200] req-e34e23d2 | qa | 14900.2ms
[200] req-36d5d1f1 | qa | 14899.3ms
```

```json
{
  "traffic": 20,
  "latency_p50": 157.0,
  "latency_p95": 2655.0,
  "latency_p99": 2655.0,
  "avg_cost_usd": 0.0021,
  "total_cost_usd": 0.042,
  "tokens_in_total": 680,
  "tokens_out_total": 2666,
  "error_breakdown": {},
  "quality_avg": 0.88
}
```

---

## 5. Individual Contributions & Evidence

### Nguyen Ngoc Hao
- [TASKS_COMPLETED]: Implemented and verified correlation ID propagation, log enrichment, PII-safe logging/tracing, Langfuse SDK v4 tracing, `/metrics` dashboard evidence, `rag_slow` incident testing, alert rule/runbook update, and final validation.
- [EVIDENCE_LINK]: Local files changed: `app/main.py`, `app/agent.py`, `app/tracing.py`, `config/alert_rules.yaml`, `docs/alerts.md`, `docs/dashboard.html`, `individual_report.md`, `docs/hao_template.md`. Commit/PR link to be added after pushing.

### [MEMBER_B_NAME]
- [TASKS_COMPLETED]:
- [EVIDENCE_LINK]:

### [MEMBER_C_NAME]
- [TASKS_COMPLETED]:
- [EVIDENCE_LINK]:

### [MEMBER_D_NAME]
- [TASKS_COMPLETED]:
- [EVIDENCE_LINK]:

### [MEMBER_E_NAME]
- [TASKS_COMPLETED]:
- [EVIDENCE_LINK]:

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Not claimed.
- [BONUS_AUDIT_LOGS]: Not claimed.
- [BONUS_CUSTOM_METRIC]: Added a lightweight local `/dashboard` view backed by `/metrics`, showing latency, traffic, error rate, cost, tokens, and quality.
