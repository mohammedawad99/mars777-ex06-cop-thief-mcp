# COSTS — Resource Awareness

Stage 0 estimates are **assumptions**, not measurements. Each is replaced with
a measured figure once the relevant stage runs. Track per-run cost in
`results/local/` (git-ignored) and summarize here.

## Cost categories

| Category | Driver | Assumption (Stage 0) | Measured |
|----------|--------|----------------------|----------|
| LLM API | Agent turns per move × moves × sub-games × 2 agents | ~thousands of tokens per match; small $ per full run | TBD |
| Cloud hosting / tunneling | Exposing MCP servers over HTTP for inter-group play | Free-tier / local tunnel; ~$0 baseline | TBD |
| Gmail API | A few report emails per submission | Within free quota; ~$0 | TBD |
| Local execution | Dev machine CPU/time | Negligible | TBD |

## Assumptions vs measured

- **Assumptions** here are deliberately conservative and may be wrong by an
  order of magnitude; do not quote them as facts in the submission.
- **Measured** values are filled in from real runs (token usage from LLM
  responses, wall-clock time, request counts) and are the numbers reported.

## Controls

- Rate limits in `config/rate_limits.default.json` cap request volume.
- `max_moves` and `num_sub_games` bound per-run cost.
- Retries are bounded (`retry_max_attempts`) to avoid runaway spend.

## Token/cost accounting model (Stage 9, fake_local)

- The LLM layer estimates tokens per prompt/response (`llm/cost.py`, ~4 chars per
  token) and an `estimated_cost_usd` from a per-1k rate. The offline `fake_local`
  provider uses a **zero rate** — it does **no real spend** — but token counts are
  computed and summed, so the accounting model is real and ready for a paid
  provider that sets a non-zero rate.
- The prompted game report carries `total_prompt_tokens_estimate`,
  `total_response_tokens_estimate`, `estimated_cost_usd`, `parse_failures`, and
  `fallbacks_used`. A measured full default game (6 sub-games) over local HTTP
  reported ≈ **24,762 prompt** + **2,574 response** token estimates,
  `estimated_cost_usd = 0.0` (fake_local).
- These are **estimates from the fake provider**, not real-provider figures. When
  a real external provider is added (opt-in, later stage), the rate and measured
  usage/cost from real responses replace the zero-rate model here.

## Dependency / hosting note (Stage 5)

- Stage 5 added **FastMCP** (`fastmcp>=3.4.2,<4`, pinned in `uv.lock`) for the
  local HTTP MCP servers. This is a development/runtime library, not a paid
  service — it adds **no direct $ cost**.
- The MCP servers run **local-only** on `127.0.0.1` (Cop `8001`, Thief `8002`);
  there is **no cloud hosting, no public URL, and no tunneling** at this stage,
  so the "Cloud hosting / tunneling" row remains a **future** assumption (~$0
  baseline). It will be revisited when cloud/public URLs are introduced.
- No LLM or Gmail calls are made by the MCP servers (the LLM lives in the future
  client), so LLM/Gmail cost rows are unchanged and still TBD.
