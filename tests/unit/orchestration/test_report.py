"""Unit tests for the in-memory report builder and totals."""

import json

from mars777_cop_thief.agents import cop_policy, thief_policy
from mars777_cop_thief.orchestration.report import build_report
from mars777_cop_thief.orchestration.runner import run_full_game
from mars777_cop_thief.orchestration.totals import win_counts


def test_report_is_json_serializable(engine, make_config):
    config = make_config()
    results = run_full_game(engine, config["num_sub_games"], cop_policy, thief_policy)
    report = build_report(config, results)
    text = json.dumps(report)
    assert isinstance(text, str)
    assert len(report["sub_games"]) == 6


def test_report_carries_identity_and_local_status(engine, make_config):
    config = make_config()
    results = run_full_game(engine, config["num_sub_games"], cop_policy, thief_policy)
    report = build_report(config, results)
    assert report["group_code"] == "MaRs-777"
    assert report["group_slug"] == "mars777"
    assert report["timezone"] == "Asia/Jerusalem"
    assert report["github_repo"] == "REPLACE_WITH_GITHUB_REPO_URL"
    assert report["stage"] == "local-self-play"
    assert report["mcp_status"] == "not-deployed"
    assert report["config"]["num_sub_games"] == 6


def test_totals_and_win_counts_consistent(engine, make_config):
    config = make_config()
    results = run_full_game(engine, config["num_sub_games"], cop_policy, thief_policy)
    report = build_report(config, results)
    counts = win_counts(results)
    assert sum(counts.values()) == 6
    assert report["totals"]["cop"] >= 0
    assert report["totals"]["thief"] >= 0
