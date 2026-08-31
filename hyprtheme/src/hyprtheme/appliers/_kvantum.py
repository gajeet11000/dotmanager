"""Generates a Kvantum theme (widget/window painting) from a raw hex
palette -- the piece that actually reaches KDE-Frameworks apps' widget
colors, since qt6ct/hyprqt6engine's own QPalette gets ignored by them.

A theme's SVG must match its own light/dark polarity -- reusing a
dark-sourced SVG for a light palette renders the window background wrong
regardless of correct kvconfig colors (confirmed live: same kvconfig,
different-polarity SVG, wrong background). Bring two base SVGs -- one
copied from any installed dark Kvantum theme, one from any installed light
one, both with zero hardcoded colors (`grep 'fill="#'` should match
nothing in either) so they're pure shape templates safe to recolor for any
palette. And a `.kvconfig.template` -- a real theme's `.kvconfig` with
every hex color replaced by an `@ROLE@` token matching build_tokens' keys
below; structure/geometry/widget-state settings untouched.
"""

import shutil
from pathlib import Path

from hyprtheme.appliers._palette import luminance, mix


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


def _render_kvconfig(template_file: Path, p: dict) -> str:
    text = template_file.read_text()
    for token, value in build_tokens(p).items():
        text = text.replace(token, value)
    return text


def write_theme(
    kvantum_dir: Path, base_svg: dict[str, Path], template_file: Path,
    theme_name: str, palette: dict,
) -> None:
    """Generate `<kvantum_dir>/<theme_name>/` for this palette."""
    theme_dir = kvantum_dir / theme_name
    theme_dir.mkdir(parents=True, exist_ok=True)

    (theme_dir / f"{theme_name}.kvconfig").write_text(_render_kvconfig(template_file, palette))
    shutil.copyfile(base_svg[palette["base"]], theme_dir / f"{theme_name}.svg")


def select_theme(kvantum_dir: Path, theme_name: str) -> None:
    """Point `<kvantum_dir>/kvantum.kvconfig` at this theme."""
    kvantum_dir.mkdir(parents=True, exist_ok=True)
    (kvantum_dir / "kvantum.kvconfig").write_text(f"[General]\ntheme={theme_name}\n")
