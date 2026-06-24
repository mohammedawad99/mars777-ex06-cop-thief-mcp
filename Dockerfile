# syntax=docker/dockerfile:1
# Single role-aware image for the two MCP servers (Cop / Thief).
# The role is selected at runtime by MCP_ROLE (cop|thief); the entrypoint binds
# 0.0.0.0 and reads PORT. No secret is baked into the image — tokens come from the
# runtime environment / secret manager. See docs/CLOUD_DEPLOYMENT.md.
FROM python:3.11-slim

# uv is the only package manager used in this project.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

# Install locked dependencies first for better layer caching.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Application code and config only (no .env / credentials / token — see .dockerignore).
COPY src ./src
COPY config ./config
COPY README.md ./
RUN uv sync --frozen --no-dev

# Cloud platform provides PORT; set MCP_ROLE=cop or MCP_ROLE=thief per service.
# MCP_ROLE is intentionally empty so a misconfigured service fails fast and clearly.
ENV MCP_ROLE=""
EXPOSE 8080

CMD ["uv", "run", "python", "-m", "mars777_cop_thief.mcp_servers.cloud_entrypoint"]
