"""Single entry point (SDK facade) for all Cop/Thief game logic.

Every external consumer (CLI, GUI, tests, notebooks) must go through this
module rather than importing orchestrator/agent/game internals directly.
"""
import asyncio
import random

from fastmcp import Client

from copthief.mcp_servers.factory import build_agent_server
from copthief.orchestrator.game_series import SeriesResult, run_game_series
from copthief.shared.config import GameConfig, load_game_config
from copthief.shared.constants import Role


class CopThiefSdk:
    """Facade that wires the two in-process MCP servers and runs full game series."""

    def __init__(self, config: GameConfig | None = None, seed: int | None = None):
        self.config = config or load_game_config()
        self._rng = random.Random(seed)
        self._cop_server = build_agent_server(Role.COP)
        self._thief_server = build_agent_server(Role.THIEF)

    async def run_series_async(self) -> SeriesResult:
        async with Client(self._cop_server) as cop_client, Client(self._thief_server) as thief_client:
            return await run_game_series(cop_client, thief_client, self.config, self._rng)

    def run_series(self) -> SeriesResult:
        """Synchronous convenience wrapper around `run_series_async` for CLI/script use."""
        return asyncio.run(self.run_series_async())
