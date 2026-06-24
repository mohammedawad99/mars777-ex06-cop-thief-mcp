# QUALITY — Gates & Checks

All gates run locally via uv before any commit. A change is "green" only when
every gate below passes.

## Gates

1. **Dependency sync** — `uv sync`
2. **Tests** — `uv run pytest`
3. **Coverage (≥ 85%)** — `uv run pytest --cov=src --cov-report=term-missing`
   (enforced by `fail_under = 85` in `pyproject.toml`)
4. **Lint** — `uv run ruff check .`
5. **Format check** — `uv run ruff format --check .`
6. **Working tree / ignore audit** — `git status --short --ignored`
7. **Secret & artifact scan** — manual review plus the ignore audit above:
   confirm no `.env`, `credentials.json`, `token.json`, keys, caches, PDFs,
   or course files are tracked.
8. **File-size gate** — every Python source file stays **< 150** non-empty,
   non-comment lines: `find src tests -name "*.py" -print0 | xargs -0 wc -l`.
9. **Local MCP HTTP E2E smoke** —
   `uv run python -m mars777_cop_thief.mcp_client.smoke` must exit 0 with all
   checks true. It starts the Cop/Thief servers as local subprocesses on free
   ports, drives them over HTTP, and tears them down. Also runs as a default
   pytest integration test (`tests/integration/mcp/`); skippable with
   `RUN_MCP_E2E=0` where local subprocesses are not permitted.

## Staging discipline

- **Never** run `git add .` — stage files explicitly and intentionally.
- Do not commit until changes have been reviewed and a commit is requested.

## Conventions

- Ruff is the single linter/formatter (line length 100).
- Tests must not contact external services or require credentials.
- Configuration is data (`config/*.default.json`), validated by the SDK.
