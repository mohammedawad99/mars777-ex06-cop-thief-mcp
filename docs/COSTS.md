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

## Cloud hosting cost & budget guard (Stage 13A)

- **Target:** Google Cloud Run — billed per request/CPU/memory with a generous
  free tier; two small, scale-to-zero MCP services for short matches are expected
  to be **within the free tier (~$0)**. This is an **assumption**, not a measured
  figure — nothing is deployed yet.
- **Budget guard:** deployment is **gated** (`RUN_CLOUD_DEPLOY=1`); the deploy
  script is inert by default and creates no resources. Scale-to-zero plus the
  bounded `num_sub_games`/`max_moves` keep any future spend small.
- **Measured cloud cost:** **TBD** — to be filled in only after a real deploy and
  a metered run; none was performed.

## Rate-limit / resource guard (Stage 12)

- A `ResourceGuard` model (`run/rate_limit.py`) reads conservative limits from
  `config/rate_limits.default.json` (MCP requests/min, max concurrent) and the
  output cap from `config/runtime.default.json` (`provider_max_output_tokens`),
  and validates they are positive — making the per-run resource budget explicit
  and auditable.
- A validated `RetryPolicy` (`run/retry.py`) sources timeouts/retries from
  `config/runtime.default.json` instead of hardcoding them; `retry_call` is
  bounded and uses an injectable sleep so it never blocks tests.

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

## Gemini cost measurement & live-smoke budget guard (Stage 10)

- The optional Gemini provider reports **actual usage tokens** from
  `usage_metadata` when available (else the estimator). `estimated_cost_usd` uses
  a per-1k rate placeholder (`GEMINI_RATE_PER_1K = 0.0`); set it to your tier's
  blended $/1k rate to price real runs — until then cost is reported as 0.0 and
  **not claimed as a measured spend**.
- **Live-smoke budget guard:** the real Gemini smoke is **gated**
  (`RUN_GEMINI_LIVE=1`), runs only **one short bounded sub-game** on a 3×3 board
  with `max_moves = 4` (a handful of calls), and caps output via
  `GEMINI_MAX_OUTPUT_TOKENS` (default 120). It is **not** a full 6-sub-game game.
- Measured real-Gemini token/cost figures are **TBD** — to be filled in only after
  a local `RUN_GEMINI_LIVE=1` run with a real key; none was run for this stage.

## Gmail API cost/resource note (Stage 11)

- The Gmail report sender uses the **Gmail API** with the minimal `gmail.send`
  scope. Sending a few report emails per submission is **within the free Gmail API
  quota** — effectively **~$0**.
- The default mode is **dry-run** (no API call, no network); a live send happens
  only with `RUN_GMAIL_LIVE=1`. No email was sent in this stage, so there is no
  measured send count/cost yet (free-tier; TBD if a live send is performed).
- Resource impact is negligible (one local OAuth flow once, then a cached token
  outside the repo).

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
