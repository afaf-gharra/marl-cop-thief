from copthief.mcp_servers.factory import _auth_provider, build_agent_server
from copthief.shared.constants import Role


def test_no_auth_provider_when_token_unset(monkeypatch):
    monkeypatch.delenv("MCP_AUTH_TOKEN", raising=False)
    assert _auth_provider() is None


def test_auth_provider_created_when_token_set(monkeypatch):
    monkeypatch.setenv("MCP_AUTH_TOKEN", "secret-token-123")
    provider = _auth_provider()
    assert provider is not None
    assert "secret-token-123" in provider.tokens


def test_server_builds_with_auth_enabled(monkeypatch):
    monkeypatch.setenv("MCP_AUTH_TOKEN", "secret-token-123")
    server = build_agent_server(Role.COP)
    assert server.auth is not None


async def test_authenticated_http_roundtrip(monkeypatch, unused_tcp_port_factory=None):
    """Full HTTP-level proof: request without token is rejected, with token succeeds."""
    import asyncio

    import httpx
    import uvicorn
    from fastmcp import Client
    from fastmcp.client.auth import BearerAuth

    monkeypatch.setenv("MCP_AUTH_TOKEN", "secret-token-123")
    server = build_agent_server(Role.THIEF)
    app = server.http_app()

    config = uvicorn.Config(app, host="127.0.0.1", port=18802, log_level="error")
    uv_server = uvicorn.Server(config)
    task = asyncio.create_task(uv_server.serve())
    try:
        while not uv_server.started:
            await asyncio.sleep(0.05)

        async with httpx.AsyncClient() as http:
            unauthorized = await http.post(
                "http://127.0.0.1:18802/mcp",
                json={"jsonrpc": "2.0", "id": 1, "method": "ping"},
                headers={"Accept": "application/json, text/event-stream"},
            )
        assert unauthorized.status_code == 401

        async with Client("http://127.0.0.1:18802/mcp", auth=BearerAuth("secret-token-123")) as client:
            tools = await client.list_tools()
        assert any(tool.name == "take_turn" for tool in tools)
    finally:
        uv_server.should_exit = True
        await task
