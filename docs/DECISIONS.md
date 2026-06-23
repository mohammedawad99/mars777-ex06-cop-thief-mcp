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
