import argparse
import sys
from pathlib import Path

from hyprtheme.manager import ThemeManager


def _build_manager(args: argparse.Namespace) -> ThemeManager:
    plugin_dirs = [Path(d).expanduser() for d in (args.plugin_dir or [])]
    return ThemeManager(
        apps_path=Path(args.apps).expanduser(),
        themes_dir=Path(args.themes_dir).expanduser(),
        plugin_dirs=plugin_dirs,
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="hyprtheme", description="Theme switcher for Hyprland and friends")
    parser.add_argument("--apps", required=True, help="Path to apps.toml")
    parser.add_argument("--themes-dir", required=True, help="Directory of theme .toml files")
    parser.add_argument(
        "--plugin-dir", action="append",
        help="Directory of local plugin .py files (repeatable)",
    )

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List available theme names")
    set_parser = sub.add_parser("set", help="Set and live-apply a theme")
    set_parser.add_argument("name")

    args = parser.parse_args()
    manager = _build_manager(args)

    if args.command == "list":
        for name in manager.list_themes():
            print(name)
    elif args.command == "set":
        try:
            manager.set_theme(args.name)
        except ValueError as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
