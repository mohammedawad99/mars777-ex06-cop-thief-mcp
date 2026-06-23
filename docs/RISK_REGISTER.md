# RISK REGISTER

**Group:** MaRs-777 (`mars777`) · **Stage:** 1 · **Status:** Baseline

Risks that threaten delivery, correctness, security, or the bonus claim. Scales:
**Impact** and **Likelihood** are `Low` / `Med` / `High`. "Trigger" is the
observable signal that the risk is materialising and the mitigation should fire.
Each risk links to related requirement IDs in `REQUIREMENTS_MATRIX.md`.

| ID | Risk | Impact | Likelihood | Mitigation | Trigger | Owner/area |
|----|------|--------|------------|------------|---------|------------|
| RK-01 | LLM inconsistency — agents produce variable/contradictory decisions | High | High | Seed runs; constrain prompts; validate every action against engine rules; retry with bounded attempts; log raw+interpreted (R-003, R-068) | Repeated illegal/contradictory actions in transcripts | Agents |
| RK-02 | Natural-language ambiguity — NL intent not cleanly interpretable | High | High | Deterministic interpreter with reject/clarify path; log ambiguity; never silently default (R-003, R-025) | Interpreter confidence low or multiple valid parses | Protocol |
| RK-03 | Token leak — auth token exposed in code, logs, or report | High | Med | Tokens via env only; redact in logs; secret scans in quality gates (R-010, R-053) | Token string appears in grep/log scan | Security |
| RK-04 | Public endpoint exposure — server reachable without auth | High | Med | Auth middleware on every tool; deny-by-default; external unauth test (R-010) | Unauthenticated request succeeds | Security/MCP |
| RK-05 | Google OAuth setup failure — consent/scope/credential misconfig | High | Med | Document setup in sender PRD; dry-run path; fallback documented method (R-037) | OAuth flow errors during sender bring-up | Email |
| RK-06 | Gmail send failure — quota, scope, or transient API error | Med | Med | Retry with backoff; dry-run + saved payload; alternative documented send (R-032, R-037) | Send returns error / non-2xx | Email |
| RK-07 | Cloud URL instability — public URL drops or rotates | High | Med | Health checks; stable hosting; capture run evidence promptly; documented restart (R-006) | URL stops responding mid-match | Cloud |
| RK-08 | Firewall / NAT issues — inbound HTTP blocked between groups | High | Med | Use a hosted/tunneled public URL; verify reachability before match window (R-006, R-007) | Foreign client cannot reach server | Cloud |
| RK-09 | Inter-group disagreement — groups disagree on the result | Med | Med | Shared logs; compare reports; `mutual_agreement` gate; dispute procedure (R-035) | Two reports differ on outcome/score | Bonus |
| RK-10 | Invalid-move dispute — contested legality of an action | Med | Med | Authoritative engine; full transcript with interpreted actions; logs decide (R-025, R-026) | A group contests a logged action | Game/Process |
| RK-11 | Overclaiming — asserting capabilities without evidence | High | Med | Evidence-first rule; every claim cites a proof artifact; matrix `Done` gate (R-065) | A doc claim lacks a linked artifact | Process |
| RK-12 | Under-tested orchestration — pipeline paths uncovered | High | Med | TDD on orchestrator; integration tests; coverage ≥ 85 focus on glue (R-051, R-058) | Coverage gaps in orchestrator modules | Quality |
| RK-13 | Late bonus coordination — other group engaged too late | High | Med | Initiate contact early; fixed match window; protocol doc ready ahead (R-007) | No partner confirmed near deadline | Bonus/Process |
| RK-14 | Hardcoding game parameters — literals creep into code | Med | Med | Central config loader; grep audit each stage; review checklist (R-013, R-055) | grep finds numeric literals in engine | Quality |
| RK-15 | Exceeding 150-line files — modules grow past limit | Med | Med | Split early; size check in gates each stage (R-052) | A file approaches the line cap | Quality |
| RK-16 | Accidental commit of credentials — OAuth/token files staged | High | Med | `.gitignore` coverage; pre-commit secret scan; no `git add .` blanket (R-036, R-053) | Secret file appears in `git status` | Security |
| RK-17 | Poor logs — insufficient detail to resolve disputes | Med | Med | Structured per-turn transcripts with raw+interpreted+result; log review (R-026) | Log lacks fields needed to reconstruct | Process |
| RK-18 | Incomplete JSON schema — report missing required fields | Med | Med | Schema-validate reports; field checklist from matrix (R-031, R-033, R-034) | Schema validation fails / field missing | Report |
| RK-19 | Running out of time — scope slips past deadline | High | Med | Staged TODO; bonus designed-in not bolted-on; cut Optional first (R-040, R-042) | Stage milestones slipping vs. calendar | Process |
| RK-20 | API cost surprises — LLM/cloud spend exceeds budget | Med | Med | Rate limits; cost tracking in `COSTS.md`; cheap models for smoke runs (R-061, R-069) | Spend trends above planned budget | Cost |
| RK-21 | Transport drift — incompatible MCP/HTTP assumptions between groups | Med | Med | HTTP from day one; interop check before match; shared protocol doc (R-004, R-007) | Foreign tool calls fail to parse | MCP/Bonus |
| RK-22 | Non-deterministic tests — flaky CI due to randomness/timing | Med | Med | Seed RNG; isolate external calls; no network in unit tests (R-068) | Tests pass/fail intermittently | Quality |
| RK-23 | Scoring drift — implemented scoring diverges from rubric | Med | Low | Scoring from config; property tests on `[30,90]` bounds (R-027–R-030) | Computed totals out of range | Game |
| RK-24 | Token revocation forgotten — bonus tokens remain live | Med | Med | Revocation step in protocol; post-game checklist (R-070) | Tokens still valid after session | Security/Bonus |

## Handling protocol

1. Any risk reaching **Impact High + Likelihood High** is escalated and tracked
   as a blocking item until reduced.
2. When a trigger is observed, the mitigation is executed and the event is logged
   in the relevant transcript or stage notes (evidence-first).
3. The register is reviewed at the start of every stage and at the final gap
   audit (`FINAL_GAP_AUDIT.md`).
