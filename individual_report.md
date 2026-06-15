# Individual Report - Day 13 Observability Lab

## 1. Thong tin ca nhan

- Ho ten: Nguyen Ngoc Hao
- Ma hoc vien: 2A202600903
- Repo/folder: `2A202600903-NguyenNgocHao-Day13`
- Chu de lab: Monitoring, Logging, and Observability for a FastAPI agent app
- Vai tro ca nhan de xuat: Logging, Correlation ID, PII Scrubbing, Validation, Evidence Collection

## 2. Muc tieu bai lab

Muc tieu cua lab la hoan thien starter app FastAPI de co day du cac thanh phan observability:

1. Structured JSON logging.
2. Correlation ID cho tung request bang header `x-request-id`.
3. Log enrichment voi user/session/feature/model context.
4. PII scrubbing de tranh lo thong tin nhay cam trong log.
5. Langfuse tracing voi toi thieu 10 traces.
6. Metrics endpoint phuc vu dashboard 6 panels.
7. Alert rules va runbook cho incident response.
8. Bao cao ca nhan va bang chung cham diem.

## 3. Ket qua thuc hien - Chay load test lan 1

Sau khi cai dependencies trong `.venv`, tao file `.env`, dien Langfuse keys va chay starter app, toi da gui 10 requests bang script `scripts/load_test.py` voi `--concurrency 5`.

Ket qua:

```text
[200] req-6bb51b0e | qa | 789.5ms
[200] req-38bb3e5f | qa | 787.4ms
[200] req-05f80871 | summary | 790.7ms
[200] req-a38a9d3c | qa | 789.6ms
[200] req-ab98365c | qa | 791.6ms
[200] req-7da14666 | summary | 157.3ms
[200] req-531c2ad1 | qa | 768.0ms
[200] req-0c25d3e9 | qa | 768.6ms
[200] req-6a1022b9 | qa | 765.1ms
[200] req-c3589b4e | qa | 769.3ms
```

Nhan xet:

- Tat ca 10 requests deu tra ve HTTP `200`, chung to app dang chay on dinh trong dieu kien request binh thuong.
- Moi response deu co correlation ID dang `req-...`, vi du `req-6bb51b0e`, `req-38bb3e5f`, `req-05f80871`.
- Latency cua phan lon request nam khoang 765-792ms; rieng mot request `summary` co latency 157.3ms, nhanh hon cac request khac.
- Ket qua nay cho thay correlation ID da duoc propagate ra response va co the dung de lien ket request voi log/trace.

## 4. Ket qua thuc hien - Validate logs

Sau khi load test, toi chay script `scripts/validate_logs.py` de kiem tra chat luong logging.

Ket qua:

```text
--- Lab Verification Results ---
Total log records analyzed: 21
Records with missing required fields: 0
Records with missing enrichment (context): 20
Unique correlation IDs found: 10
Potential PII leaks detected: 0

--- Grading Scorecard (Estimates) ---
+ [PASSED] Basic JSON schema
+ [PASSED] Correlation ID propagation
- [FAILED] Log enrichment (missing user_id_hash, etc.)
+ [PASSED] PII scrubbing

Estimated Score: 80/100
```

Nhan xet:

- Basic JSON schema da pass: log records da co cac field co ban nhu timestamp, level va event.
- Correlation ID propagation da pass: script tim thay 10 correlation IDs khac nhau tu 10 requests.
- PII scrubbing da pass: script khong phat hien email, credit card test hoac PII tho trong logs.
- Log enrichment chua pass: co 20 records thieu context fields nhu `user_id_hash`, `session_id`, `feature`, `model`.
- Diem tam thoi dat `80/100`, da dat nguong passing toi thieu cua rubric, nhung chua hoan hao vi con thieu log enrichment.

## 5. Ket qua thuc hien - Gui them requests de tao traces

Toi tiep tuc gui them 10 requests bang `scripts/load_test.py --concurrency 5` de tang so luong traffic/logs/traces cho he thong.

Ket qua:

```text
[200] req-2256d880 | summary | 799.9ms
[200] req-9e5fa776 | qa | 800.3ms
[200] req-526f7174 | qa | 803.6ms
[200] req-59ccc5b0 | qa | 805.6ms
[200] req-bf6436ac | qa | 804.2ms
[200] req-ea672d1a | summary | 158.6ms
[200] req-3b3678ac | qa | 771.0ms
[200] req-97219e8c | qa | 770.2ms
[200] req-413c79d4 | qa | 768.7ms
[200] req-c34b2676 | qa | 769.8ms
```

Nhan xet:

- Tat ca requests tiep tuc thanh cong voi HTTP `200`.
- He thong da co tong cong it nhat 20 requests thanh cong tu hai lan load test.
- Neu Langfuse keys trong `.env` hoat dong dung, luong request nay du de tao toi thieu 10 traces theo passing criteria.
- Latency binh thuong van on dinh quanh 770-805ms, voi mot request `summary` nhanh hon o muc 158.6ms.

## 6. Ket qua thuc hien - Incident test voi `rag_slow`

Toi da bat incident `rag_slow` de mo phong tinh huong RAG/retrieval bi cham.

Lenh bat incident tra ve:

```text
200 {'ok': True, 'incidents': {'rag_slow': True, 'tool_fail': False, 'cost_spike': False}}
```

Sau do toi chay lai load test:

```text
[200] req-f059bac5 | qa | 13278.2ms
[200] req-480e03b3 | qa | 13283.2ms
[200] req-62bdf1d3 | summary | 13283.3ms
[200] req-08fd38f3 | qa | 13282.2ms
[200] req-62fe7ba3 | qa | 13285.9ms
[200] req-989f6aa1 | summary | 2660.3ms
[200] req-5cea4936 | qa | 10625.3ms
[200] req-abaf81ef | qa | 13279.9ms
[200] req-241a87a6 | qa | 13281.2ms
[200] req-73003c10 | qa | 13278.9ms
```

Sau khi test xong, toi tat incident:

```text
200 {'ok': True, 'incidents': {'rag_slow': False, 'tool_fail': False, 'cost_spike': False}}
```

Nhan xet:

- Incident `rag_slow` da duoc bat thanh cong va tat thanh cong.
- Trong dieu kien binh thuong, latency chu yeu nam khoang 770-805ms.
- Khi bat `rag_slow`, phan lon request tang len khoang 13.2s, co request 10.6s va mot request `summary` 2.66s.
- Day la dau hieu ro rang cua tail latency degradation, phu hop voi alert `high_latency_p95`.
- Root cause tam thoi co the gan voi incident toggle `rag_slow`, tuc phan retrieval/RAG bi lam cham co chu dich.
- Ket qua nay co the dung lam evidence cho phan Incident Response: symptoms la latency tang manh, root cause la `rag_slow`, fix action la disable incident toggle.

## 7. Ket qua thuc hien - Fix log enrichment va validate lai

Sau khi bo sung log enrichment trong endpoint `/chat`, toi chay lai `scripts/load_test.py --concurrency 5`.

Ket qua load test:

```text
[200] req-925f4d6e | summary | 640.7ms
[200] req-b7ead67d | qa | 799.4ms
[200] req-567bb445 | qa | 796.5ms
[200] req-b6350c70 | qa | 796.5ms
[200] req-04d7c675 | qa | 801.5ms
[200] req-45c39f8d | summary | 312.7ms
[200] req-fcfd871b | qa | 777.4ms
[200] req-aca5ef75 | qa | 777.4ms
[200] req-2ff01257 | qa | 776.0ms
[200] req-6f5b077d | qa | 775.4ms
```

Sau do toi chay `scripts/validate_logs.py`.

Ket qua validate:

```text
--- Lab Verification Results ---
Total log records analyzed: 20
Records with missing required fields: 0
Records with missing enrichment (context): 0
Unique correlation IDs found: 10
Potential PII leaks detected: 0

--- Grading Scorecard (Estimates) ---
+ [PASSED] Basic JSON schema
+ [PASSED] Correlation ID propagation
+ [PASSED] Log enrichment
+ [PASSED] PII scrubbing

Estimated Score: 100/100
```

Nhan xet:

- Tat ca 10 requests deu thanh cong voi HTTP `200`.
- Script validate doc duoc 20 log records, tuong ung voi 10 requests va cac log event lien quan.
- `Records with missing required fields` bang 0, chung to JSON log schema da day du.
- `Records with missing enrichment` bang 0, chung to cac API logs da co context fields can thiet.
- `Unique correlation IDs found` bang 10, dung voi so request da gui trong lan test.
- `Potential PII leaks detected` bang 0, chung to PII scrubbing van hoat dong sau khi them enrichment.
- Diem validate tang tu `80/100` len `100/100`. Phan logging hien da dat day du cac muc: JSON schema, correlation ID, enrichment va PII scrubbing.

## 8. Ket qua thuc hien - Langfuse tracing

Sau khi sua instrumentation theo Langfuse SDK hien tai, toi chay lai app voi `LANGFUSE_DEBUG=True` va gui request vao endpoint `/chat`. Server in ra debug log cho thay trace da duoc tao va flush thanh cong.

Mot trace mau:

```text
trace_id: d57beff0d5bfd545fc9260610b6d7f32
root span: agent-run
child generation: fake-llm-generate
session_id: s06
user_id: 4c4f62330d76
tags: lab, summary, claude-sonnet-4-5
model: claude-sonnet-4-5
latency_ms: 151
quality_score: 0.9
```

Server log cho thay root span `agent-run` va child span `fake-llm-generate` cung nam trong cung mot trace:

```text
Trace: Processing span name='fake-llm-generate'
trace_id: d57beff0d5bfd545fc9260610b6d7f32
parent_id: 3e519ec1185327dd

Trace: Processing span name='agent-run'
trace_id: d57beff0d5bfd545fc9260610b6d7f32
parent_id: null

Successfully flushed OTEL tracer provider
Successfully flushed score ingestion queue
Successfully flushed media upload queue
```

Toi tiep tuc kiem tra truc tiep bang Langfuse API. API tra ve trace thanh cong voi du lieu:

```text
id='d57beff0d5bfd545fc9260610b6d7f32'
name='chat-request'
session_id='s06'
user_id='4c4f62330d76'
tags=['claude-sonnet-4-5', 'lab', 'summary']
latency=0.152
total_cost=0.001323
projectId='cmqf9xv1i03cnad0cfwt4imzl'
html_path='/project/cmqf9xv1i03cnad0cfwt4imzl/traces/d57beff0d5bfd545fc9260610b6d7f32'
```

API list trace gan nhat cung tra ve:

```text
total_items=20
total_pages=2
```

Nhan xet:

- Langfuse tracing da hoat dong tren backend: trace da duoc ingest va co the query lai qua API.
- Moi request tao trace ten `chat-request`, co root span `agent-run` va child generation `fake-llm-generate`.
- Trace co day du user/session/tags/model/token usage/cost/latency metadata.
- PII trong trace input da duoc redact, vi du email thanh `[REDACTED_EMAIL]`, phone thanh `[REDACTED_PHONE_VN]`, credit card thanh `[REDACTED_CREDIT_CARD]`.
- UI Langfuse ban dau van hien "Waiting for first trace" khi dung SDK cu `langfuse==3.2.1`. Sau khi nang SDK len `langfuse==4.7.1` va sua instrumentation theo API moi, traces da hien thi tren UI.
- Link truc tiep de mo trace mau tren Langfuse: `https://cloud.langfuse.com/project/cmqf9xv1i03cnad0cfwt4imzl/traces/d57beff0d5bfd545fc9260610b6d7f32`.

## 9. Trang thai hien tai

Sau cac buoc tren, trang thai hien tai cua lab:

- App chay thanh cong trong moi truong `.venv`.
- Load test thanh cong voi HTTP `200`.
- Correlation ID da xuat hien trong response.
- Validate logs dat `100/100`.
- JSON schema, correlation ID, log enrichment va PII scrubbing da pass.
- Langfuse da ingest `20` traces va UI da hien thi trace sau khi nang SDK; trace mau co root span, child generation, metadata va usage/cost.
- Incident `rag_slow` da duoc test va cho thay latency tang ro ret.

## 10. Cac muc se cap nhat tiep

Cac muc duoi day se duoc bo sung sau khi co them output/evidence:

- Metrics snapshot tu endpoint `/metrics`.
- Screenshot/dashboard 6 panels.
- Alert rules va evidence test alert.
- Phan tong ket dong gop ca nhan cuoi cung.
