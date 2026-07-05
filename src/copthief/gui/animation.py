"""Real-time-style GUI: an animated, turn-by-turn playback of one sub-game.

Renders cop/thief positions and every barrier as it is placed, frame per
turn, and saves it as a looping GIF — the closest thing to a live GUI that
still works headlessly (no display required) for grading/CI.
"""
from pathlib import Path

from copthief.orchestrator.sub_game import SubGameRecord

_COP_COLOR = "tab:blue"
_THIEF_COLOR = "tab:red"
_BARRIER_COLOR = "black"


def _frame_barriers(record: SubGameRecord, up_to_turn: int) -> list[list[int]]:
    return [t.barrier_placed for t in record.turns[: up_to_turn + 1] if t.barrier_placed is not None]


def render_sub_game_gif(
    record: SubGameRecord,
    grid_size: tuple[int, int],
    output_path: str,
    interval_ms: int = 500,
) -> Path:
    """Save an animated GIF showing the full turn-by-turn sub-game playback."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter

    rows, cols = grid_size
    fig, ax = plt.subplots(figsize=(4, 4))
    frames = max(len(record.turns), 1)

    def _draw(turn_index: int) -> None:
        ax.clear()
        ax.set_xlim(-0.5, cols - 0.5)
        ax.set_ylim(-0.5, rows - 0.5)
        ax.set_xticks(range(cols))
        ax.set_yticks(range(rows))
        ax.invert_yaxis()
        ax.grid(True)
        ax.set_title(f"Turn {min(turn_index + 1, len(record.turns))}/{len(record.turns)} — {record.outcome}")

        for barrier in _frame_barriers(record, turn_index):
            ax.scatter(barrier[1], barrier[0], marker="X", s=180, color=_BARRIER_COLOR, label="barrier")

        cop_pos, thief_pos = None, None
        for turn in record.turns[: turn_index + 1]:
            if turn.role == "cop":
                cop_pos = turn.position_after
            else:
                thief_pos = turn.position_after
        if cop_pos:
            ax.scatter(cop_pos[1], cop_pos[0], marker="s", s=220, color=_COP_COLOR, label="cop")
        if thief_pos:
            ax.scatter(thief_pos[1], thief_pos[0], marker="o", s=220, color=_THIEF_COLOR, label="thief")

        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles, strict=True))
        ax.legend(by_label.values(), by_label.keys(), loc="upper right", fontsize=8)

    anim = FuncAnimation(fig, _draw, frames=frames, interval=interval_ms)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    anim.save(str(path), writer=PillowWriter(fps=max(1000 // interval_ms, 1)))
    plt.close(fig)
    return path


def render_live_window(record: SubGameRecord, grid_size: tuple[int, int], interval_ms: int = 500) -> None:
    """Best-effort live playback in an interactive window (needs a display; no-op headless)."""
    import matplotlib.pyplot as plt

    try:
        from matplotlib.animation import FuncAnimation
    except ImportError:
        return

    rows, cols = grid_size
    fig, ax = plt.subplots(figsize=(4, 4))

    def _draw(turn_index: int) -> None:
        ax.clear()
        ax.set_xlim(-0.5, cols - 0.5)
        ax.set_ylim(-0.5, rows - 0.5)
        ax.invert_yaxis()
        ax.grid(True)
        for barrier in _frame_barriers(record, turn_index):
            ax.scatter(barrier[1], barrier[0], marker="X", s=180, color=_BARRIER_COLOR)
        for turn in record.turns[: turn_index + 1]:
            color = _COP_COLOR if turn.role == "cop" else _THIEF_COLOR
            marker = "s" if turn.role == "cop" else "o"
            ax.scatter(turn.position_after[1], turn.position_after[0], marker=marker, s=60, color=color, alpha=0.3)

    anim = FuncAnimation(fig, _draw, frames=max(len(record.turns), 1), interval=interval_ms, repeat=False)
    try:
        plt.show()
    except Exception:  # noqa: BLE001 - headless environments have no display backend
        pass
    finally:
        plt.close(fig)
    del anim
