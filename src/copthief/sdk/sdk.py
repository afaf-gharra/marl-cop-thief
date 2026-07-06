"""Single entry point (SDK facade) for all Cop/Thief game logic.

Every external consumer (CLI, GUI, tests, notebooks) must go through this
module rather than importing orchestrator/agent/game internals directly.
Supports two modes: in-process servers (default, offline-friendly) and
remote streamable-HTTP servers (localhost-on-ports or cloud deployment).
"""
import asyncio
import random

from fastmcp import Client
from fastmcp.client.auth import BearerAuth

from copthief.mcp_servers.factory import build_agent_server
from copthief.orchestrator.game_series import SeriesResult, run_game_series
from copthief.shared.config import GameConfig, load_game_config
from copthief.shared.constants import Role


class CopThiefSdk:
    """Facade that wires the two MCP servers (in-process or remote) and runs full game series."""

    def __init__(self, config: GameConfig | None = None, seed: int | None = None):
        self.config = config or load_game_config()
        self._rng = random.Random(seed)
        self._cop_target = build_agent_server(Role.COP, self.config)
        self._thief_target = build_agent_server(Role.THIEF, self.config)
        self._auth_token: str | None = None

    @classmethod
    def from_urls(
        cls,
        cop_url: str,
        thief_url: str,
        auth_token: str | None = None,
        config: GameConfig | None = None,
        seed: int | None = None,
    ) -> "CopThiefSdk":
        """Build an SDK that talks to already-running MCP servers over HTTP (local or cloud)."""
        sdk = cls.__new__(cls)
        sdk.config = config or load_game_config()
        sdk._rng = random.Random(seed)
        sdk._cop_target = cop_url
        sdk._thief_target = thief_url
        sdk._auth_token = auth_token
        return sdk

    def _client(self, target) -> Client:
        auth = BearerAuth(self._auth_token) if self._auth_token and isinstance(target, str) else None
        return Client(target, auth=auth)

    async def run_series_async(self) -> SeriesResult:
        async with self._client(self._cop_target) as cop_client, self._client(self._thief_target) as thief_client:
            return await run_game_series(cop_client, thief_client, self.config, self._rng)

    def run_series(self) -> SeriesResult:
        """Synchronous convenience wrapper around `run_series_async` for CLI/script use."""
        return asyncio.run(self.run_series_async())
