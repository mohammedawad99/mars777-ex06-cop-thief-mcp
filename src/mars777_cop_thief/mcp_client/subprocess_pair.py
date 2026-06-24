"""Start/stop the local Cop and Thief MCP servers as subprocesses for smoke E2E.

Servers bind to 127.0.0.1 on free ports; tokens and ports are injected via the
child process environment (never committed). Processes are always terminated in
the context manager's ``finally`` block.
"""

from __future__ import annotations

import contextlib
import socket
import subprocess
import sys
from collections.abc import Iterator


def free_port() -> int:
    """Pick an available local TCP port."""
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def child_env(base_env: dict, token_var: str, token: str, port_var: str, port: int) -> dict:
    """Copy ``base_env`` and inject the role token + port (no real secrets)."""
    env = dict(base_env)
    env[token_var] = token
    env[port_var] = str(port)
    return env


def _spawn(module: str, env: dict) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, "-m", f"mars777_cop_thief.mcp_servers.{module}"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def terminate(proc: subprocess.Popen) -> None:
    """Terminate a process, escalating to kill if it does not exit."""
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()


@contextlib.contextmanager
def server_pair(cop_token: str, thief_token: str) -> Iterator[dict]:
    """Run both local servers on free ports; yield URLs; always tear down."""
    import os

    cop_port, thief_port = free_port(), free_port()
    cop_env = child_env(os.environ, "COP_MCP_TOKEN", cop_token, "COP_MCP_PORT", cop_port)
    thief_env = child_env(os.environ, "THIEF_MCP_TOKEN", thief_token, "THIEF_MCP_PORT", thief_port)
    cop_proc, thief_proc = _spawn("run_cop", cop_env), _spawn("run_thief", thief_env)
    try:
        yield {
            "cop_url": f"http://127.0.0.1:{cop_port}/mcp",
            "thief_url": f"http://127.0.0.1:{thief_port}/mcp",
            "cop_port": cop_port,
            "thief_port": thief_port,
        }
    finally:
        terminate(cop_proc)
        terminate(thief_proc)
