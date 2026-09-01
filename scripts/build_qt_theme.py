#!/usr/bin/env python3
"""One-off maintenance tool -- NOT part of the `main.py` CLI.

Generates every theme's Kvantum widget theme + KDE .colors file from its
[palette] table in themes/<name>/theme.toml, writing them into that same
theme's own themes/<name>/qt/ folder. Qt theming needs a whole rendered
theme, not a value substitution like kitty/waybar -- but a theme's palette
is a fixed preset, nothing computed at runtime, so this renders it once,
here; core/theme_appliers/qt_theme.py just symlinks to the result at
`theme set` time. No color math happens on every switch.

Covers the fixed set of themes dotmanager actually uses -- rerun this only
if one of their [palette] values changes. Safe to rerun any time -- it
regenerates every theme's output from scratch, so nothing goes stale.

base-dark.svg and base-light.svg (assets/kvantum/) are pure-shape SVG
templates (verified `grep 'fill="#'` matches nothing in either), copied
from real installed Kvantum themes matching each polarity -- see
core/theme_appliers/qt_theme.py's docstring for how Kvantum/kdeglobals/
hyprqt6engine fit together. base.kvconfig.template is a real theme's
.kvconfig with every hex color replaced by an @ROLE@ token (see
build_tokens() below for the exact set) -- reused across every theme.
"""

import shutil
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.theme_appliers._palette import luminance, mix  # noqa: E402
from core.theme_appliers.qt_theme import theme_name  # noqa: E402

THEMES_DIR = REPO_ROOT / "themes"
BASE_SVG = {
    "dark": REPO_ROOT / "assets" / "kvantum" / "base-dark.svg",
    "light": REPO_ROOT / "assets" / "kvantum" / "base-light.svg",
}
TEMPLATE_FILE = REPO_ROOT / "assets" / "kvantum" / "base.kvconfig.template"


def build_tokens(p: dict) -> dict:
    bg, fg, accent, muted = p["bg"], p["fg"], p["accent"], p["muted"]
    return {
        "@WINDOW@": bg,
        "@BASE@": mix(bg, "#000000", 0.12),
        "@BUTTON@": mix(bg, fg, 0.08),
        "@LIGHT@": mix(bg, fg, 0.15),
        "@HIGHLIGHT_ALPHA@": accent + "4d",  # ~30% alpha, matches the source theme
        "@TEXT@": fg,
        "@MUTED@": muted,
        "@DIM_TEXT@": mix(fg, bg, 0.35),
        "@ACCENT@": accent,
        "@LINK_VISITED@": p["purple"],
        "@ON_ACCENT@": "#000000" if luminance(accent) > 0.5 else "#ffffff",
    }


def _kvconfig(p: dict) -> str:
    text = TEMPLATE_FILE.read_text()
    for token, value in build_tokens(p).items():
        text = text.replace(token, value)
    return text


def _build_kvantum(theme_dir: Path, name: str, p: dict) -> None:
    kvantum_dir = theme_dir / "qt" / name
    kvantum_dir.mkdir(parents=True, exist_ok=True)
    (kvantum_dir / f"{name}.kvconfig").write_text(_kvconfig(p))
    shutil.copyfile(BASE_SVG[p["base"]], kvantum_dir / f"{name}.svg")


def _rgb(hex_color: str) -> str:
    return ",".join(str(int(hex_color[i : i + 2], 16)) for i in (1, 3, 5))


def _section(bg_normal: str, fg_normal: str, p: dict) -> str:
    bg, fg, accent, muted = p["bg"], p["fg"], p["accent"], p["muted"]
    return (
        f"BackgroundAlternate={_rgb(mix(bg_normal, fg_normal, 0.06))}\n"
        f"BackgroundNormal={_rgb(bg_normal)}\n"
        f"DecorationFocus={_rgb(accent)}\n"
        f"DecorationHover={_rgb(mix(accent, fg, 0.2))}\n"
        f"ForegroundActive={_rgb(accent)}\n"
        f"ForegroundInactive={_rgb(muted)}\n"
        f"ForegroundLink={_rgb(p['blue'])}\n"
        f"ForegroundNegative={_rgb(p['red'])}\n"
        f"ForegroundNeutral={_rgb(p['yellow'])}\n"
        f"ForegroundNormal={_rgb(fg_normal)}\n"
        f"ForegroundPositive={_rgb(p['green'])}\n"
        f"ForegroundVisited={_rgb(p['purple'])}\n"
    )


def _selection_section(p: dict) -> str:
    bg, fg, accent, muted = p["bg"], p["fg"], p["accent"], p["muted"]
    on_accent = "#000000" if luminance(accent) > 0.5 else "#ffffff"
    return (
        f"BackgroundAlternate={_rgb(accent)}\nBackgroundNormal={_rgb(accent)}\n"
        f"DecorationFocus={_rgb(accent)}\nDecorationHover={_rgb(mix(accent, fg, 0.2))}\n"
        f"ForegroundActive={_rgb(on_accent)}\nForegroundInactive={_rgb(on_accent)}\n"
        f"ForegroundLink={_rgb(p['blue'])}\nForegroundNegative={_rgb(p['red'])}\n"
        f"ForegroundNeutral={_rgb(p['yellow'])}\nForegroundNormal={_rgb(on_accent)}\n"
        f"ForegroundPositive={_rgb(p['green'])}\nForegroundVisited={_rgb(p['purple'])}\n"
    )


def _colors_file(name: str, p: dict) -> str:
    bg, fg, muted = p["bg"], p["fg"], p["muted"]
    button_bg = mix(bg, fg, 0.08)
    view_bg = mix(bg, "#000000", 0.08)
    tooltip_bg = mix(bg, "#000000", 0.20)
    inactive_bg = mix(bg, fg, 0.03)

    return (
        "[ColorEffects:Disabled]\n"
        f"Color={_rgb(muted)}\n"
        "ColorAmount=0\nColorEffect=0\nContrastAmount=0.65\nContrastEffect=1\n"
        "IntensityAmount=0.1\nIntensityEffect=0\n\n"
        "[ColorEffects:Inactive]\n"
        "ChangeSelectionColor=true\n"
        f"Color={_rgb(muted)}\n"
        "ColorAmount=0.025\nColorEffect=2\nContrastAmount=0.1\nContrastEffect=2\n"
        "Enable=true\nIntensityAmount=0\nIntensityEffect=0\n\n"
        f"[Colors:Button]\n{_section(button_bg, fg, p)}\n"
        f"[Colors:Selection]\n{_selection_section(p)}\n"
        f"[Colors:Tooltip]\n{_section(tooltip_bg, fg, p)}\n"
        f"[Colors:View]\n{_section(view_bg, fg, p)}\n"
        f"[Colors:Window]\n{_section(bg, fg, p)}\n"
        "[General]\n"
        f"ColorScheme={name}\nName={name}\nshadeSortColumn=true\n\n"
        "[KDE]\ncontrast=0\n\n"
        "[WM]\n"
        f"activeBackground={_rgb(bg)}\nactiveBlend={_rgb(bg)}\nactiveForeground={_rgb(fg)}\n"
        f"inactiveBackground={_rgb(inactive_bg)}\ninactiveBlend={_rgb(inactive_bg)}\ninactiveForeground={_rgb(muted)}\n"
    )


def _build_colors(theme_dir: Path, name: str, p: dict) -> None:
    qt_dir = theme_dir / "qt"
    qt_dir.mkdir(parents=True, exist_ok=True)
    (qt_dir / f"{name}.colors").write_text(_colors_file(name, p))


def main() -> None:
    for path in sorted(THEMES_DIR.glob("*/theme.toml")):
        data = tomllib.loads(path.read_text())
        theme = data.get("name", path.parent.name)
        palette = data.get("palette")
        if palette is None:
            print(f"'{theme}' has no [palette], skipping")
            continue

        name = theme_name(theme)
        print(f"Building Qt assets for '{theme}' -> {path.parent}/qt/")
        _build_kvantum(path.parent, name, palette)
        _build_colors(path.parent, name, palette)

    print("Done.")


if __name__ == "__main__":
    main()
