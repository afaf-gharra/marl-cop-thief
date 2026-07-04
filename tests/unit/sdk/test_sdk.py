from copthief.sdk.sdk import CopThiefSdk


def test_run_series_returns_configured_number_of_sub_games(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    sdk = CopThiefSdk(seed=1)
    result = sdk.run_series()
    assert len(result.sub_games) == sdk.config.num_games
    assert result.cop_total >= 0
    assert result.thief_total >= 0
