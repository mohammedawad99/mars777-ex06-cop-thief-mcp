"""Deterministic run identity and config fingerprinting.

A run id is derived only from group/stage/config-hash/seed, so the same config
and seed always yield the same id. Timestamp and git commit are injectable for
deterministic tests. No secret is ever included.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime

from mars777_cop_thief.constants import GROUP_CODE, GROUP_SLUG
from mars777_cop_thief.shared.version import __version__

_AUTO = "__auto__"


@dataclass(frozen=True)
class RunIdentity:
    """Stable, secret-free identity for one run."""

    run_id: str
    group_code: str
    group_slug: str
    stage: str
    mode: str
    config_hash: str
    seed: int
    created_at_utc: str
    git_commit: str | None
    package_version: str
    cloud_status: str

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "group_code": self.group_code,
            "group_slug": self.group_slug,
            "stage": self.stage,
            "mode": self.mode,
            "config_hash": self.config_hash,
            "seed": self.seed,
            "created_at_utc": self.created_at_utc,
            "git_commit": self.git_commit,
            "package_version": self.package_version,
            "cloud_status": self.cloud_status,
        }


def config_fingerprint(config: dict) -> str:
    """Stable short hash of a config (order-independent)."""
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _utc_now() -> str:  # pragma: no cover - wall clock
    return datetime.now(UTC).isoformat()


def _git_commit() -> str | None:  # pragma: no cover - environment dependent
    try:
        done = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5
        )
        return done.stdout.strip() if done.returncode == 0 else None
    except Exception:
        return None


def build_run_identity(
    config: dict,
    *,
    stage: str,
    mode: str,
    seed: int = 0,
    created_at_utc: str | None = None,
    git_commit: str | None = _AUTO,
    cloud_status: str = "not_deployed",
) -> RunIdentity:
    """Build a deterministic run identity (id excludes the timestamp)."""
    fingerprint = config_fingerprint(config)
    slug = config.get("group_slug", GROUP_SLUG)
    return RunIdentity(
        run_id=f"{slug}-{stage}-{fingerprint}-seed{seed}",
        group_code=config.get("group_code", GROUP_CODE),
        group_slug=slug,
        stage=stage,
        mode=mode,
        config_hash=fingerprint,
        seed=seed,
        created_at_utc=created_at_utc if created_at_utc is not None else _utc_now(),
        git_commit=_git_commit() if git_commit == _AUTO else git_commit,
        package_version=__version__,
        cloud_status=cloud_status,
    )
