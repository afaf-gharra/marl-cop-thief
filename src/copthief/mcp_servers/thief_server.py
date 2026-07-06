"""Independent MCP server for the Thief agent. Run standalone: `uv run python -m copthief.mcp_servers.thief_server`.

Host binds to 127.0.0.1 by default; set MCP_HOST=0.0.0.0 to expose it (e.g. on a cloud VM).
"""
from copthief.mcp_servers.factory import build_agent_server
from copthief.shared.config import get_env
from copthief.shared.constants import THIEF_MCP_PORT, Role

app = build_agent_server(Role.THIEF)

if __name__ == "__main__":
    app.run(transport="http", host=get_env("MCP_HOST", "127.0.0.1"), port=THIEF_MCP_PORT)
