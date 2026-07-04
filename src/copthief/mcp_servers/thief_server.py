"""Independent MCP server for the Thief agent. Run standalone: `uv run python -m copthief.mcp_servers.thief_server`."""
from copthief.mcp_servers.factory import build_agent_server
from copthief.shared.constants import THIEF_MCP_PORT, Role

app = build_agent_server(Role.THIEF)

if __name__ == "__main__":
    app.run(transport="http", host="127.0.0.1", port=THIEF_MCP_PORT)
