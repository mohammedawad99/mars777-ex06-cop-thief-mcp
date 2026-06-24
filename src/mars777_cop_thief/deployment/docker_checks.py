"""Static checks over the Docker packaging (no Docker daemon, no network).

Confirms the Dockerfile and .dockerignore exist, that the ignore list covers the
files that must never enter an image, and that no forbidden secret file is present
in the repository tree.
"""

from __future__ import annotations

import os
from pathlib import Path

REQUIRED_DOCKERIGNORE = (
    ".git",
    ".venv",
    ".env",
    "credentials.json",
    "token.json",
    "__pycache__",
    ".coverage",
)

_FORBIDDEN_NAMES = (
    "credentials.json",
    "token.json",
    "token.pickle",
    ".env",
    "service_account.json",
)
_FORBIDDEN_SUFFIXES = (".key", ".pem", ".p12")
_EXCLUDE_DIRS = (".git", ".venv", ".ruff_cache", ".pytest_cache", "node_modules")


def dockerfile_exists(root: Path) -> bool:
    return (root / "Dockerfile").is_file()


def dockerignore_exists(root: Path) -> bool:
    return (root / ".dockerignore").is_file()


def dockerignore_patterns(root: Path) -> list[str]:
    text = (root / ".dockerignore").read_text(encoding="utf-8")
    return [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]


def missing_dockerignore_entries(root: Path) -> list[str]:
    patterns = dockerignore_patterns(root) if dockerignore_exists(root) else []
    joined = "\n".join(patterns)
    return [required for required in REQUIRED_DOCKERIGNORE if required not in joined]


def find_forbidden_secret_files(root: Path) -> list[str]:
    """Return relative paths of any committed-style secret files found under ``root``."""
    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _EXCLUDE_DIRS]
        for name in filenames:
            if name in _FORBIDDEN_NAMES or name.endswith(_FORBIDDEN_SUFFIXES):
                found.append(str(Path(dirpath, name).relative_to(root)))
    return found
