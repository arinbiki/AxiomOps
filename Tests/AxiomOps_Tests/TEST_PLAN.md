# AxiomOps Test Plan
## Production Readiness Verification

**Suite:** AxiomOps (Compliance Control Operations Suite)  
**Target:** n8n Self-Hosted + PostgreSQL + Ollama  
**Test Date:** ___________  
**Tester:** ___________  
**Environment:** ___________  

---

## Philosophy

This test suite is designed for **vibe coders** who architect systems but do not write syntax-heavy code. Every test is:

- **Copy-paste ready** into GitHub Copilot Chat
- **Self-verifying** via SQL (the database is the source of truth)
- **3B-model safe** (one task per prompt, exact commands, no ambiguity)
- **MCP-compatible** (Copilot can execute these via your n8n connection)

---

## Test Pyramid

```
       /\
      /  \
     / 4  \     Failure Mode Tests (security, resilience)
    /--------\
   /    3     \   Stress Tests (bulk, concurrency)
  /------------\
 /      2       \  Smoke Tests (end-to-end flows)
/----------------\
/        1        \ Unit Tests (individual workflows)
/-------------------\
/         0          \ Setup & Health Checks
-----------------------
```

---

## Phase 0: Environment Setup (Required before all tests)

| # | Test | What It Does | Pass Criteria |
|---|------|--------------|---------------|
| 0.1 | Database Reset | Truncates all operational tables | `findings` count = 0 |
| 0.2 | Workflow Health | Lists all 11 workflows in n8n | All 11 names found |

**Why this matters:** Every test below assumes a clean slate. If you skip reset, occurrence counts will be wrong.

---

## Phase 1: Unit Tests (Individual Workflow Verification)

| # | Workflow | Test | What It Verifies |
|---|----------|------|------------------|
| 1.1 | 01 Registry Sync | Valid payload upserts assets + controls | 2 assets, 2 controls in DB |
| 1.2 | 02 Finding Ingestion | Failed control creates finding | `status='open'`, `occurrence_count=1` |
| 1.3 | 03 Owner Resolver | Asset owner resolved correctly | `owner_status='resolved_asset_owner'` |
| 1.4 | 04 Risk Prioritizer | Score, priority, SLA calculated | `risk_score > 0`, priority is P1-P4 |
| 1.5 | 05 Remediation Orchestrator | Ticket created and linked | `remediation_tasks` row exists |
| 1.6 | 08 Closure Validator | Passed evidence closes finding | `status='closed'`, `closed_at` set |
| 1.7 | 09 Ollama Assistant | AI returns text or fails safely | `aiStatus` present, no crash |

**Unit test rule:** Each test runs in isolation and verifies database state via SQL. We do not trust HTTP responses alone.

---

## Phase 2: Smoke Tests (End-to-End Flows)

| # | Flow | Tests |
|---|------|-------|
| 2.1 | Full Lifecycle | Registry → Failed Finding → Owner → Risk → Ticket → Passed → Closure |
| 2.2 | Exception Lifecycle | Request → Approve → Finding becomes `risk_accepted` → New failed evidence blocked from ticket creation |
| 2.3 | Missing Owner Fallback | No asset owner + no control default → fallback admin assigned |

**Smoke test rule:** These test the **wiring between workflows**, not just individual logic.

---

## Phase 3: Stress Tests

| # | Test | Load | Pass Criteria |
|---|------|------|---------------|
| 3.1 | Bulk Ingestion | 50 sequential findings | 50 evidence rows, 1 ticket (no duplicates) |
| 3.2 | Concurrent Exceptions | 10 exception requests | All 10 created with unique IDs |

**Stress test rule:** Your VPS has 24GB RAM. We stay sequential to avoid n8n queue overload.

---

## Phase 4: Failure Mode Tests

| # | Scenario | What We Break | Expected Behavior |
|---|----------|---------------|-------------------|
| 4.1 | Invalid Auth Token | Send wrong X-COMPLIANCEOPS-TOKEN | HTTP error, no DB writes |
| 4.2 | Duplicate Prevention | Same runId + findingKey twice | 1 evidence row, 1 occurrence |
| 4.3 | AI Unavailable | Ollama stopped | Core workflows complete, fallback text used |
| 4.4 | SLA Differentiation | Critical prod vs High dev | Critical gets P1 + shorter SLA |

**Failure mode rule:** The system must **degrade gracefully**. Never crash the core lifecycle because of a side feature.

---

## How to Run

### Option A: Copilot Chat (Recommended for Vibe Coders)

1. Open GitHub Copilot Chat in VS Code
2. Copy **one** prompt from `COPILOT_PROMPTS.md`
3. Paste and press Enter
4. Wait for the JSON result
5. Record PASS/FAIL in the checklist below
6. Move to the next prompt

### Option B: Python Test Runner

```bash
cd "D:\web project\AxiomOps\Tests"
pip install -r requirements.txt
python scripts/test_runner.py --phase unit
python scripts/test_runner.py --phase smoke
python scripts/test_runner.py --phase stress
python scripts/test_runner.py --phase failure
python scripts/test_runner.py --all
```

### Option C: Manual (curl + psql)

Use the fixtures in `fixtures/` and verification queries in `SQL_VERIFICATION.md`.

---

## Production Readiness Checklist

Check each box only after the test shows PASS:

- [ ] 0.1 Database Reset works
- [ ] 0.2 All 11 workflows exist
- [ ] 1.1 Registry Sync (valid payload)
- [ ] 1.2 Finding Ingestion (failed control)
- [ ] 1.3 Owner Resolver (asset owner found)
- [ ] 1.4 Risk Prioritizer (score + SLA set)
- [ ] 1.5 Remediation Orchestrator (ticket created)
- [ ] 1.6 Closure Validator (finding closed on pass)
- [ ] 1.7 Ollama Assistant (safe fallback)
- [ ] 2.1 Full Lifecycle (end-to-end)
- [ ] 2.2 Exception Flow (approve + block)
- [ ] 2.3 Missing Owner Fallback
- [ ] 3.1 Bulk Ingestion (50 findings)
- [ ] 4.1 Invalid Auth blocked
- [ ] 4.2 Duplicate Prevention
- [ ] 4.3 AI Unavailable survival
- [ ] 4.4 SLA Differentiation

**If ALL required tests pass, AxiomOps is production-ready.**

---

## Interpreting Failures

| Failure Pattern | Likely Cause | Fix |
|-----------------|--------------|-----|
| HTTP 404 on webhook | Workflow not activated | Activate workflow in n8n |
| Postgres connection error | Wrong credentials | Check .env or n8n settings |
| `occurrence_count` too high | Database not reset | Run test 0.1 first |
| `owner_status` = unresolved | Registry sync failed | Re-run test 1.1 |
| Ticket not created | Exception active? Jira down? | Check exceptions table, Jira config |
| Finding not closed | Closure validator not triggered | Check 08 is active, check evidence_events |
| AI test FAILs | Ollama not running | This is OK if 4.3 passes (core logic survives) |

---

## Files Reference

| File | Purpose |
|------|---------|
| `fixtures/*.json` | Sample payloads for every test scenario |
| `scripts/test_runner.py` | Automated Python test harness |
| `COPILOT_PROMPTS.md` | Copy-paste prompts for Copilot Chat |
| `SQL_VERIFICATION.md` | Exact queries to verify database state |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |

---

## Notes for 3B Model Users

**Why these prompts work with small models:**

1. **One task per prompt** — 3B models lose context after ~2-3 steps
2. **Exact SQL provided** — No room for hallucinating table names
3. **Expected JSON format** — Forces structured output
4. **DO NOT sections** — Prevents common mistakes (modifying workflows, skipping SQL)
5. **Correction prompts** — Ready-to-use when the model drifts

**If Copilot Chat gets confused:**
- Paste the CORRECTION PROMPT from `COPILOT_PROMPTS.md`
- Start a **new chat session** for each phase
- Use the Python runner instead for bulk tests

---

## Sign-Off

**Production Ready:** ___ Yes  ___ No  
**Date:** ___________  
**Signed By:** ___________  
**Blockers:** ___________
