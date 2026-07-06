"""Edge-case coverage for the MCP game loop: technical-loss handling and the
boxed-in 'pass' branch. Uses a fake MCP client so no server/network is needed."""
import random

import pytest

from copthief.orchestrator.sub_game import run_sub_game
from copthief.shared.constants import Outcome


class _FakeResult:
    def __init__(self, data):
        self.data = data


class _RaisingClient:
    """A client whose take_turn always fails — should become a technical loss."""

    async def call_tool(self, name, args):
        raise RuntimeError("simulated MCP failure")


@pytest.mark.asyncio
async def test_run_sub_game_maps_failure_to_technical_loss(small_config):
    record = await run_sub_game(_RaisingClient(), _RaisingClient(), small_config, random.Random(0))
    assert record.outcome == Outcome.TECHNICAL_LOSS.value
    assert record.score is None


class _PassiveClient:
    """Always tells the agent to move up; used to drive a full survival game."""

    async def call_tool(self, name, args):
        if name == "report_outcome":
            return _FakeResult({"acknowledged": True})
        return _FakeResult({"message": "up", "action": "up"})


@pytest.mark.asyncio
async def test_run_sub_game_completes_survival_when_no_capture(small_config):
    record = await run_sub_game(_PassiveClient(), _PassiveClient(), small_config, random.Random(1))
    assert record.outcome in (Outcome.THIEF_WINS.value, Outcome.COP_WINS.value)
    assert record.score is not None
    assert len(record.turns) <= small_config.max_moves
