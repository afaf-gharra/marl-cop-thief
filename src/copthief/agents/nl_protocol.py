"""Free natural-language protocol layer: builds prompts, parses replies, and provides an
offline deterministic fallback so tests never depend on a live LLM (per submission guidelines)."""
import random
import re

from copthief.shared.constants import Action, Role

_ACTION_TAG = re.compile(r"ACTION:\s*(\w+)", re.IGNORECASE)

_ROLE_FLAVOR = {
    Role.COP: "You are the Cop, hunting the Thief on a grid. Be terse and tactical.",
    Role.THIEF: "You are the Thief, evading the Cop on a grid. Be terse and evasive.",
}


def build_prompt(
    role: Role,
    partial_view: dict,
    incoming_message: str,
    legal_actions: list[Action],
    suggested_action: Action,
) -> str:
    """Compose the LLM prompt: interpret the opponent's message, infer their position,
    then translate to one of the legal grid actions (the three steps required by the spec)."""
    action_names = ", ".join(a.value for a in legal_actions)
    return (
        f"{_ROLE_FLAVOR[role]}\n"
        f"Your position: {partial_view['own_position']}. Grid size: {partial_view['grid_size']}.\n"
        f"Turn: {partial_view['turn_count']}. Opponent distance hint: {partial_view['distance_hint']}.\n"
        f"Opponent's last message: \"{incoming_message}\"\n"
        f"1. Interpret what the opponent's message implies about their plan.\n"
        f"2. Infer their likely position or direction from that message and the distance hint.\n"
        f"3. Choose ONE action from: [{action_names}]. Our optimizer suggests '{suggested_action.value}' "
        f"but you may override it if the message changes your assessment.\n"
        f"Reply with a short free-text message to the opponent, then a final line exactly "
        f"'ACTION: <action_name>'."
    )


def parse_reply(text: str, legal_actions: list[Action], fallback: Action) -> tuple[str, Action]:
    """Extract the free-text message and the chosen action from an LLM reply."""
    match = _ACTION_TAG.search(text)
    message = _ACTION_TAG.sub("", text).strip()
    if not match:
        return message or text.strip(), fallback
    try:
        candidate = Action(match.group(1).lower())
    except ValueError:
        return message, fallback
    return message, candidate if candidate in legal_actions else fallback


_FALLBACK_TEMPLATES = {
    Role.COP: [
        "Closing in from {own_position}, moving {action}.",
        "I see barriers near me; advancing {action} to corner you.",
        "Distance is {distance_hint}; I'm going {action}.",
    ],
    Role.THIEF: [
        "Slipping away, heading {action} from {own_position}.",
        "You're {distance_hint}; I'm breaking {action} to open ground.",
        "Staying evasive, moving {action}.",
    ],
}


def template_fallback(
    role: Role,
    partial_view: dict,
    suggested_action: Action,
    rng: random.Random | None = None,
) -> tuple[str, Action]:
    """Deterministic-ish offline message generator used when no LLM API key is configured."""
    rng = rng or random.Random()
    template = rng.choice(_FALLBACK_TEMPLATES[role])
    message = template.format(
        own_position=partial_view["own_position"],
        distance_hint=partial_view["distance_hint"],
        action=suggested_action.value,
    )
    return message, suggested_action
