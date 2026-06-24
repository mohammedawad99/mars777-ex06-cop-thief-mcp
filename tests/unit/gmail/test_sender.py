"""Unit tests for the Gmail senders (dry-run + mocked live; no network)."""

import json

from mars777_cop_thief.gmail.config import load_gmail_config
from mars777_cop_thief.gmail.sender import DryRunGmailSender, GmailApiSender


class _Send:
    def __init__(self, message_id):
        self._id = message_id

    def execute(self):
        return {"id": self._id}


class _Messages:
    def __init__(self, message_id, calls):
        self._id = message_id
        self._calls = calls

    def send(self, *, userId, body):
        self._calls.append({"userId": userId, "body_keys": sorted(body)})
        return _Send(self._id)


class _Users:
    def __init__(self, message_id, calls):
        self._messages = _Messages(message_id, calls)

    def messages(self):
        return self._messages


class _Service:
    def __init__(self, message_id, calls):
        self._users = _Users(message_id, calls)

    def users(self):
        return self._users


def test_dry_run_does_not_call_api_and_validates(report):
    result = DryRunGmailSender(load_gmail_config()).send(report, env={})
    assert result.status == "dry_run"
    assert result.body_json_valid is True
    assert result.validation_errors == []
    assert result.gmail_message_id is None


def test_dry_run_rejects_invalid_report():
    bad = {"report_type": "internal_game"}  # missing required fields
    result = DryRunGmailSender(load_gmail_config()).send(bad, env={})
    assert result.status == "failed"
    assert result.validation_errors


def test_non_serializable_report_marks_body_invalid():
    # A complete-looking report whose value cannot be JSON-serialized.
    bad = {"report_type": "internal_game", "weird": {1, 2, 3}}
    result = DryRunGmailSender(load_gmail_config()).send(bad, env={})
    assert result.body_json_valid is False
    assert result.status == "failed"


def test_result_has_no_secret_fields(report):
    result = DryRunGmailSender(load_gmail_config()).send(report, env={})
    serialized = json.dumps(result.to_dict()).lower()
    for secret in ("token", "credential", "api_key", "client_secret", "/google/"):
        assert secret not in serialized


def test_live_sender_maps_message_id(report):
    calls = []
    sender = GmailApiSender(
        load_gmail_config(), service_factory=lambda creds: _Service("gmail-msg-123", calls)
    )
    result = sender.send(report, creds=object(), env={})
    assert result.status == "sent"
    assert result.gmail_message_id == "gmail-msg-123"
    assert calls and calls[0]["userId"] == "me"
    assert calls[0]["body_keys"] == ["raw"]


def test_live_sender_rejects_invalid_report_before_sending():
    calls = []
    sender = GmailApiSender(load_gmail_config(), service_factory=lambda creds: _Service("x", calls))
    result = sender.send({"report_type": "internal_game"}, creds=object(), env={})
    assert result.status == "failed"
    assert calls == []  # never reached the API
