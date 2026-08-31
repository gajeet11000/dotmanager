"""Generates a Kvantum theme (widget/window painting) per dotmanager theme.

Kvantum is what actually reaches KDE-Frameworks apps' widget colors --
qt6ct/hyprqt6engine's own QPalette gets ignored by them (see qt_theme.py's
docstring for how that was confirmed). This module owns everything
Kvantum-specific: generating each theme's .kvconfig from the shared
template + this palette's colors, pairing it with the SVG matching the
theme's light/dark polarity, and pointing kvantum.kvconfig at it.

base-dark.svg and base-light.svg (assets/kvantum/) are copied verbatim
from the system-installed `catppuccin-macchiato-mauve` (dark) and
`catppuccin-latte-blue` (light) Kvantum themes -- both confirmed to have
zero hardcoded colors (`grep fill=\"#` matches nothing in either), so
each is a pure shape template safe to recolor for any palette sharing
its base. They are NOT interchangeable: a dark-sourced SVG renders a
light palette's window background wrong (verified live via a byte-
identical-except-colors kvconfig -- the SVG, not the kvconfig, was the
difference), so the SVG must match the theme's own `base`.

base.kvconfig.template is the dark theme's .kvconfig with every one of
its hex colors replaced by an @ROLE@ token (see build_tokens below) --
structure/geometry/widget-state settings untouched, only recolored per
dotmanager theme. The template is shared across both SVGs since the
only kvconfig difference between the two source themes (once colors are
masked) was the `comment=` line.
"""

import shutil
from pathlib import Path

from core.theme_appliers._palette import luminance, mix

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BASE_SVG = {
    "dark": REPO_ROOT / "assets" / "kvantum" / "base-dark.svg",
    "light": REPO_ROOT / "assets" / "kvantum" / "base-light.svg",
}
TEMPLATE_FILE = REPO_ROOT / "assets" / "kvantum" / "base.kvconfig.template"

KVANTUM_DIR = Path.home() / ".config" / "Kvantum"
MAIN_CONF = KVANTUM_DIR / "kvantum.kvconfig"


def theme_name(dotmanager_theme: str) -> str:
    return f"dotmanager-{dotmanager_theme}"


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


def _render_kvconfig(p: dict) -> str:
    text = TEMPLATE_FILE.read_text()
    for token, value in build_tokens(p).items():
        text = text.replace(token, value)
    return text


def write_theme(dotmanager_theme: str, palette: dict) -> None:
    """Generate ~/.config/Kvantum/dotmanager-<name>/ for this palette."""
    name = theme_name(dotmanager_theme)
    theme_dir = KVANTUM_DIR / name
    theme_dir.mkdir(parents=True, exist_ok=True)

    (theme_dir / f"{name}.kvconfig").write_text(_render_kvconfig(palette))
    shutil.copyfile(BASE_SVG[palette["base"]], theme_dir / f"{name}.svg")


def select_theme(dotmanager_theme: str) -> None:
    """Point ~/.config/Kvantum/kvantum.kvconfig at this theme."""
    KVANTUM_DIR.mkdir(parents=True, exist_ok=True)
    MAIN_CONF.write_text(f"[General]\ntheme={theme_name(dotmanager_theme)}\n")
