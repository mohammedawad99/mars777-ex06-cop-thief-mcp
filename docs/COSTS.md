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
