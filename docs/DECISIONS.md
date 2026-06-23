# DECISIONS — Architecture Decision Records

Lightweight ADRs. Status: Accepted unless noted.

## ADR-0001 — Ubuntu terminal + Claude Code workflow
**Context:** Need a reproducible, scriptable dev environment for an AI-assisted
build. **Decision:** Develop on an Ubuntu terminal driven by the Claude Code
workflow. **Consequences:** All steps expressible as shell commands; easy to
document and reproduce; aligns with the course's vibe-coding approach.

## ADR-0002 — uv as the only package manager
**Context:** Multiple Python tooling options exist. **Decision:** Use **uv**
exclusively; forbid pip, `python -m`, requirements.txt, virtualenv, and venv.
**Consequences:** Single lockfile and managed environment; consistent installs
(`uv sync`) and execution (`uv run`); simpler reviewer reproduction.

## ADR-0003 — HTTP for MCP communication from the beginning
**Context:** MCP supports multiple transports; inter-group play needs a network
boundary. **Decision:** Use **HTTP transport** for all MCP communication from
day one, with token auth. **Consequences:** Inter-group play works without
re-architecting; clear auth boundary; slightly more setup than stdio.

## ADR-0004 — Separate official group code from technical slug
**Context:** The official identifier `MaRs-777` is not a clean package name.
**Decision:** Keep **`MaRs-777`** as the official group code and **`mars777`**
as the technical slug (package/module name). **Consequences:** Valid Python
identifiers; both values stored in `constants.py` and config as single truth.

## ADR-0005 — Bonus treated as mandatory scope, implemented after baseline
**Context:** Inter-group play is a bonus but affects architecture. **Decision:**
Treat inter-group play as **mandatory for architecture/planning**, but implement
it only **after a stable baseline** (engine + MCP + agents working in-group).
**Consequences:** HTTP/token boundary designed up front (see ADR-0003); avoids
late rework while not blocking the core path.

## ADR-0006 — Google OAuth credentials kept outside Git
**Context:** The report sender uses Google/Gmail OAuth. **Decision:** Never
commit `credentials.json`, `token.json`, or any OAuth artifact; reference them
via env vars and `.env`; provide placeholders in `.env-example`. **Consequences:**
No secret leakage; clear revoke story in `SECURITY.md`; CI/tests never need
credentials.

## ADR-0007 — Requirements Matrix as the audit backbone
**Context:** The assignment is graded strictly against professional practice, and
prior feedback flagged weak, unevidenced requirement tracking. **Decision:**
Maintain `docs/REQUIREMENTS_MATRIX.md` as the single audit backbone — every
requirement carries an ID, source, priority, planned response, proof artifact,
validation method, risk, and status. **Consequences:** Acceptance criteria and
the risk register reference matrix IDs one-to-one; reviewers can trace any
requirement to its evidence; "Status" is the only volatile column.

## ADR-0008 — Bonus treated as architecture-mandatory scope
**Context:** Inter-group play is officially a bonus but reshapes the network/auth
boundary if added late. **Decision:** Treat the bonus as **mandatory for
architecture and planning** (HTTP transport, token auth, config-driven foreign
URLs designed up front), implemented after a stable in-group baseline.
**Consequences:** No late re-architecture; reinforces ADR-0003/ADR-0005; the
bonus report schema is planned alongside the internal report.

## ADR-0009 — Free-language messages plus interpreted-action logs
**Context:** Agents must communicate in free natural language, yet disputes need
an unambiguous record of what actually happened. **Decision:** Agents exchange
**free natural language**; a deterministic interpreter maps each message to a
concrete engine action, and **both** the raw text and the `interpreted_action`
are logged per turn. **Consequences:** Satisfies the NL requirement while keeping
the engine authoritative; transcripts are sufficient to resolve invalid-move
disputes; ambiguous messages are rejected/clarified, never silently defaulted.

## ADR-0010 — Operational inter-group protocol separated from agent language
**Context:** "Protocol" is ambiguous — it could mean a wire format between agents
or coordination between teams. **Decision:** Keep
`docs/INTERGROUP_BONUS_PROTOCOL.md` strictly **operational** (URL/token exchange,
agreed board/origin/turn order, 3+3 role-swapped sub-games, report
reconciliation, token revocation); it imposes **no** hardcoded message protocol
on the agents, which still speak free natural language. **Consequences:** The
bonus is reproducible and fair without compromising the NL requirement;
infrastructure concerns are documented apart from game language.

## ADR-0011 — Evidence-first submission strategy
**Context:** Prior feedback flagged overclaiming and unevidenced claims.
**Decision:** Every quality or capability claim must cite a concrete proof
artifact (results JSON, transcript, validation output, or screenshot for
cloud/GUI evidence); a matrix requirement may only be marked `Done` once its
proof exists and its validation has been run. **Consequences:** No
"production-ready"/"fully implemented" language without evidence; the final gap
audit checks claim→artifact links; partial work stays `In progress`.
