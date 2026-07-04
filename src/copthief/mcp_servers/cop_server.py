"""Independent MCP server for the Cop agent. Run standalone: `uv run python -m copthief.mcp_servers.cop_server`."""
from copthief.mcp_servers.factory import build_agent_server
from copthief.shared.constants import COP_MCP_PORT, Role

app = build_agent_server(Role.COP)

if __name__ == "__main__":
    app.run(transport="http", host="127.0.0.1", port=COP_MCP_PORT)
