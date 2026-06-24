"""Unit tests for the server-lifecycle helpers (no real servers started)."""

from mars777_cop_thief.mcp_client.subprocess_pair import child_env, free_port, terminate


def test_free_port_is_a_usable_local_port():
    port = free_port()
    assert isinstance(port, int)
    assert 1024 < port < 65536


def test_child_env_injects_token_and_port_without_real_secrets():
    base = {"PATH": "/usr/bin", "HOME": "/home/x"}
    env = child_env(base, "COP_MCP_TOKEN", "dummy-cop", "COP_MCP_PORT", 9001)
    assert env["COP_MCP_TOKEN"] == "dummy-cop"
    assert env["COP_MCP_PORT"] == "9001"
    assert env["PATH"] == "/usr/bin"  # base preserved
    # Only the dummy token we passed is present — no other token value injected.
    assert "dummy-cop" in env.values()
    assert base.get("COP_MCP_TOKEN") is None  # base dict untouched


class _FakeProc:
    def __init__(self, raise_on_wait=False):
        self.terminated = False
        self.killed = False
        self._raise = raise_on_wait

    def terminate(self):
        self.terminated = True

    def wait(self, timeout=None):
        if self._raise:
            raise TimeoutError("still running")

    def kill(self):
        self.killed = True


def test_terminate_stops_process_cleanly():
    proc = _FakeProc()
    terminate(proc)
    assert proc.terminated
    assert not proc.killed


def test_terminate_escalates_to_kill_on_timeout():
    proc = _FakeProc(raise_on_wait=True)
    terminate(proc)
    assert proc.terminated
    assert proc.killed
