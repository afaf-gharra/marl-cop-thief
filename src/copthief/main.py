"""CLI entry point: runs one full 6-sub-game series locally and writes the report + a plot.

Usage: uv run python -m copthief.main
"""
from copthief.gui.animation import render_sub_game_gif
from copthief.gui.console_view import render_ascii_summary, save_final_positions_plot
from copthief.reporting.json_report import build_internal_game_report, write_report
from copthief.sdk.sdk import CopThiefSdk
from copthief.shared.constants import COP_MCP_PORT, THIEF_MCP_PORT


def main() -> None:
    sdk = CopThiefSdk(seed=42)
    result = sdk.run_series()

    for index, sub_game in enumerate(result.sub_games, start=1):
        print(render_ascii_summary(sub_game, index))
        gif_path = render_sub_game_gif(sub_game, sdk.config.grid_size, f"results/sub_game_{index}.gif")
        print(f"  (animated playback: {gif_path})\n")

    print(f"TOTALS -> cop: {result.cop_total}, thief: {result.thief_total}")

    report = build_internal_game_report(
        result,
        sdk.config,
        github_repo="https://github.com/afaf-gharra/marl-cop-thief",
        cop_mcp_url=f"http://127.0.0.1:{COP_MCP_PORT}",
        thief_mcp_url=f"http://127.0.0.1:{THIEF_MCP_PORT}",
        students=["afaf gharra (208123232)"],
    )
    write_report(report, "results/game_report.json")
    save_final_positions_plot(result.sub_games, sdk.config.grid_size, "results/final_positions.png")
    print("Wrote results/game_report.json, results/final_positions.png, and per-game GIFs")


if __name__ == "__main__":
    main()
