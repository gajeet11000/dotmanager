"""`hyprtheme-build qt <theme.toml> ...` -- generates the Kvantum theme and
KDE `.colors` file for one theme, from its `[palette]` table. Run once, by
hand, when adding a new theme; hyprtheme's own `theme set` never calls
this. See hyprtheme's README, "Adding a new theme".
"""

import argparse
import sys
from pathlib import Path

from hyprtheme.theme import load_theme

from hyprtheme_build.kcolorscheme import write_scheme
from hyprtheme_build.kvantum import render_theme


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="hyprtheme-build", description="Build-time asset generator for hyprtheme themes"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    qt_parser = sub.add_parser(
        "qt", help="Generate the Kvantum theme + KDE .colors file for one theme"
    )
    qt_parser.add_argument("theme", help="Path to the theme's .toml file")
    qt_parser.add_argument("--base-svg-dark", required=True)
    qt_parser.add_argument("--base-svg-light", required=True)
    qt_parser.add_argument("--kvconfig-template", required=True)
    qt_parser.add_argument("--kvantum-out", required=True, help="Output dir for the Kvantum theme folder")
    qt_parser.add_argument("--colors-out", required=True, help="Output dir for the .colors file")

    args = parser.parse_args()
    if args.command == "qt":
        _build_qt(args)


def _build_qt(args: argparse.Namespace) -> None:
    theme = load_theme(Path(args.theme).expanduser())
    if theme.palette is None:
        print(f"theme '{theme.name}' has no [palette], nothing to build", file=sys.stderr)
        sys.exit(1)

    theme_name = f"hyprtheme-{theme.name}"
    base_svg = {
        "dark": Path(args.base_svg_dark).expanduser(),
        "light": Path(args.base_svg_light).expanduser(),
    }
    kvconfig_template = Path(args.kvconfig_template).expanduser()
    kvantum_out = Path(args.kvantum_out).expanduser()
    colors_out = Path(args.colors_out).expanduser()

    theme_dir = render_theme(kvantum_out, base_svg, kvconfig_template, theme_name, theme.palette)
    colors_path = write_scheme(colors_out, theme_name, theme.palette)

    print(f"wrote {theme_dir}/")
    print(f"wrote {colors_path}")


if __name__ == "__main__":
    main()
