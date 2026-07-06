"""CLI entry point: runs one full 6-sub-game series and writes the report + visuals.

Usage:
    uv run python -m copthief.main                       # in-process local mode
    uv run python -m copthief.main --cop-url http://<host>:8801/mcp \
        --thief-url http://<host>:8802/mcp [--auth-token <token>]   # remote/cloud mode
"""
import argparse

from copthief.agents.llm_client import usage_tracker
from copthief.gui.animation import render_sub_game_gif
from copthief.gui.console_view import render_ascii_summary, save_final_positions_plot
from copthief.reporting.json_report import build_internal_game_report, write_report
from copthief.sdk.sdk import CopThiefSdk
from copthief.shared.config import get_env
from copthief.shared.constants import COP_MCP_PORT, THIEF_MCP_PORT


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Cop/Thief MCP game series.")
    parser.add_argument("--cop-url", help="Remote cop MCP server URL (default: in-process)")
    parser.add_argument("--thief-url", help="Remote thief MCP server URL (default: in-process)")
    parser.add_argument("--auth-token", help="Bearer token for remote servers (or MCP_AUTH_TOKEN env)")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed for reproducibility")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    remote = bool(args.cop_url and args.thief_url)
    if remote:
        token = args.auth_token or get_env("MCP_AUTH_TOKEN")
        sdk = CopThiefSdk.from_urls(args.cop_url, args.thief_url, auth_token=token, seed=args.seed)
        cop_url, thief_url = args.cop_url, args.thief_url
    else:
        sdk = CopThiefSdk(seed=args.seed)
        cop_url = f"http://127.0.0.1:{COP_MCP_PORT}"
        thief_url = f"http://127.0.0.1:{THIEF_MCP_PORT}"

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
        cop_mcp_url=cop_url,
        thief_mcp_url=thief_url,
        students=["afaf gharra (208123232)"],
    )
    write_report(report, "results/game_report.json")
    save_final_positions_plot(result.sub_games, sdk.config.grid_size, "results/final_positions.png")
    print("Wrote results/game_report.json, results/final_positions.png, and per-game GIFs")

    if usage_tracker.calls > 0:
        summary = usage_tracker.summary()
        write_report(summary, "results/llm_usage.json")
        print(f"LLM usage: {summary}")


if __name__ == "__main__":
    main()
