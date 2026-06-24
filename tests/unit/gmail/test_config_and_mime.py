"""Unit tests for Gmail config loading and the JSON-only MIME builder."""

import base64
import json

import pytest

from mars777_cop_thief.gmail.config import (
    GmailConfigError,
    load_gmail_config,
    resolve_paths,
    resolve_recipient,
)
from mars777_cop_thief.gmail.mime_builder import (
    build_body,
    build_raw_message,
    decode_raw,
    extract_json_body,
)


def test_config_loads_recipient_and_scope():
    config = load_gmail_config()
    assert config["recipient"] == "rmisegal+uoh26b@gmail.com"
    assert config["send_scope"] == "https://www.googleapis.com/auth/gmail.send"
    assert config["default_mode"] == "dry_run"
    assert config["body_format"] == "json_only"


def test_config_does_not_require_oauth_files():
    config = load_gmail_config()
    # Resolving paths from an empty env yields None without touching the filesystem.
    assert resolve_paths(config, env={}) == (None, None)
    assert resolve_recipient(config, env={}) == "rmisegal+uoh26b@gmail.com"


def test_missing_required_field_raises(tmp_path):
    bad = tmp_path / "gmail.json"
    bad.write_text(json.dumps({"version": "1.00", "recipient": "x@y.z"}), encoding="utf-8")
    with pytest.raises(GmailConfigError, match="missing gmail config fields"):
        load_gmail_config(bad)


def test_recipient_env_override():
    config = load_gmail_config()
    env = {"GMAIL_REPORT_RECIPIENT": "other@example.com"}
    assert resolve_recipient(config, env) == "other@example.com"


def test_body_is_valid_json(report):
    assert json.loads(build_body(report)) == report


def test_body_parses_back_to_report(report):
    raw = build_raw_message("to@example.com", "Subject line", report)
    assert extract_json_body(raw) == report


def test_body_has_no_greeting_or_signature(report):
    raw = build_raw_message("to@example.com", "Subject line", report)
    body = decode_raw(raw).get_content().strip()
    assert body == build_body(report)  # exactly the JSON, nothing prepended/appended
    assert body.startswith("{")
    for noise in ("Dear", "Hello", "Regards", "Sincerely", "```"):
        assert noise not in body


def test_raw_message_is_base64url(report):
    raw = build_raw_message("to@example.com", "Subject line", report)
    # Decodes as base64url and round-trips the recipient header.
    decoded = base64.urlsafe_b64decode(raw.encode("ascii"))
    assert b"to@example.com" in decoded
    assert decode_raw(raw)["To"] == "to@example.com"
