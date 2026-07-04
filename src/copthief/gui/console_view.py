"""Minimal ASCII + matplotlib visualization of a sub-game (kept out of the coverage gate,
since it is display-only and not business logic per the SDK-layer separation)."""
from pathlib import Path

from copthief.orchestrator.sub_game import SubGameRecord


def render_ascii_summary(record: SubGameRecord, index: int) -> str:
    """Render a compact, human-readable transcript of one sub-game."""
    lines = [f"--- Sub-game {index}: {record.outcome} ---"]
    for turn in record.turns:
        lines.append(f"[{turn.role:>5}] -> {turn.position_after} ({turn.action}): {turn.message}")
    if record.score:
        lines.append(f"Score -> cop: {record.score.cop_points}, thief: {record.score.thief_points}")
    return "\n".join(lines)


def save_final_positions_plot(records: list[SubGameRecord], grid_size: tuple[int, int], output_path: str) -> None:
    """Save a simple scatter plot of each sub-game's final cop/thief positions to a PNG."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.set_xlim(-0.5, grid_size[1] - 0.5)
    ax.set_ylim(-0.5, grid_size[0] - 0.5)
    ax.set_xticks(range(grid_size[1]))
    ax.set_yticks(range(grid_size[0]))
    ax.grid(True)
    ax.set_title("Final position per sub-game (last turn of each role)")

    for record in records:
        cop_turns = [t for t in record.turns if t.role == "cop"]
        thief_turns = [t for t in record.turns if t.role == "thief"]
        if cop_turns:
            row, col = cop_turns[-1].position_after
            ax.scatter(col, row, marker="s", color="blue")
        if thief_turns:
            row, col = thief_turns[-1].position_after
            ax.scatter(col, row, marker="o", color="red")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
