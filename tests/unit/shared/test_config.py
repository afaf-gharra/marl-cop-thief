import json

import pytest

from copthief.shared.config import get_env, load_game_config, load_rate_limits


def test_load_game_config_reads_repo_config():
    config = load_game_config()
    assert config.grid_size == (5, 5)
    assert config.max_moves == 25
    assert config.num_games == 6
    assert config.scoring.cop_win == 20


def test_load_rate_limits_reads_repo_config():
    limits = load_rate_limits()
    assert limits["services"]["llm"]["requests_per_minute"] == 20


def test_load_game_config_rejects_incompatible_version(tmp_path):
    bad_config = {
        "version": "2.00",
        "grid_size": [5, 5],
        "max_moves": 25,
        "num_games": 6,
        "max_barriers": 5,
        "scoring": {"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5},
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(bad_config), encoding="utf-8")
    with pytest.raises(ValueError):
        load_game_config(str(path))


def test_get_env_default(monkeypatch):
    monkeypatch.delenv("COPTHIEF_TEST_VAR", raising=False)
    assert get_env("COPTHIEF_TEST_VAR", "fallback") == "fallback"
    monkeypatch.setenv("COPTHIEF_TEST_VAR", "value")
    assert get_env("COPTHIEF_TEST_VAR") == "value"
