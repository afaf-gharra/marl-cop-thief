from copthief.gui.animation import render_sub_game_gif
from copthief.orchestrator.sub_game import SubGameRecord, TurnRecord


def test_render_sub_game_gif_writes_file(tmp_path):
    record = SubGameRecord(
        outcome="cop_wins",
        turns=[
            TurnRecord(role="thief", message="run", action="up", position_after=[0, 1]),
            TurnRecord(role="cop", message="chase", action="right", position_after=[1, 1],
                       barrier_placed=[1, 2]),
            TurnRecord(role="thief", message="caught", action="down", position_after=[0, 1]),
        ],
    )
    output_path = tmp_path / "demo.gif"

    result_path = render_sub_game_gif(record, grid_size=(3, 3), output_path=str(output_path))

    assert result_path.exists()
    assert result_path.stat().st_size > 0
