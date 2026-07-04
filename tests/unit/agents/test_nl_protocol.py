import random

from copthief.agents.nl_protocol import build_prompt, parse_reply, template_fallback
from copthief.shared.constants import Action, Role

_VIEW = {
    "role": "cop",
    "own_position": [1, 1],
    "grid_size": [5, 5],
    "barriers": [],
    "turn_count": 2,
    "barriers_remaining": 5,
    "distance_hint": "close",
}


def test_build_prompt_includes_key_fields():
    prompt = build_prompt(Role.COP, _VIEW, "I'm running north", [Action.UP, Action.DOWN], Action.UP)
    assert "running north" in prompt
    assert "up" in prompt
    assert "ACTION:" in prompt


def test_parse_reply_extracts_message_and_action():
    text = "I think you're cornered.\nACTION: left"
    message, action = parse_reply(text, legal_actions=[Action.LEFT, Action.RIGHT], fallback=Action.RIGHT)
    assert "cornered" in message
    assert action == Action.LEFT


def test_parse_reply_falls_back_on_illegal_action():
    text = "Going for it.\nACTION: up"
    message, action = parse_reply(text, legal_actions=[Action.LEFT], fallback=Action.LEFT)
    assert action == Action.LEFT


def test_parse_reply_falls_back_when_tag_missing():
    text = "No tag here."
    message, action = parse_reply(text, legal_actions=[Action.LEFT], fallback=Action.LEFT)
    assert message == "No tag here."
    assert action == Action.LEFT


def test_template_fallback_returns_suggested_action():
    message, action = template_fallback(Role.THIEF, _VIEW, Action.DOWN, rng=random.Random(1))
    assert action == Action.DOWN
    assert isinstance(message, str) and message
