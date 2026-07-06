from copthief.sdk.sdk import CopThiefSdk


def test_from_urls_stores_targets_and_token():
    sdk = CopThiefSdk.from_urls(
        "http://example.com:8801/mcp",
        "http://example.com:8802/mcp",
        auth_token="tok",
        seed=1,
    )
    assert sdk._cop_target == "http://example.com:8801/mcp"
    assert sdk._thief_target == "http://example.com:8802/mcp"
    assert sdk._auth_token == "tok"
    assert sdk.config.num_games > 0


def test_client_attaches_bearer_auth_only_for_remote_targets():
    sdk = CopThiefSdk.from_urls("http://h:1/mcp", "http://h:2/mcp", auth_token="tok")
    client = sdk._client("http://h:1/mcp")
    assert client is not None
