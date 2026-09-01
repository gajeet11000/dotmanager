"""Applies a theme profile's herdr (terminal multiplexer) UI theme.

herdr's config.toml holds keybindings and other UI settings alongside
theme, so this can't do a blanket file replace like kitty/swaync/lsd --
it surgically replaces just the [theme] block (and any
[theme.custom]/[theme.custom.light]/[theme.custom.dark] sub-tables under
it), leaving the rest of the user's config.toml untouched. Reloads via
`herdr server reload-config`, which herdr's own docs confirm applies UI
settings (including theme) live without restarting panes.

Note: v0.8.0 has no `sidebar_bg` override -- herdr's own docs say the
sidebar then "keeps the host terminal background", so its color follows
whatever kitty_theme.py set kitty to, not this file. herdr's own
[theme.custom] still controls the accent/tab-highlight colors directly
(verified live: switching themes recolors the active-tab highlight even
with kitty's background held constant).

Each profile below names the closest built-in herdr theme (herdr ships
catppuccin, gruvbox, one-light, and others, but nothing "macchiato" or
"github" specifically -- see src/config/theme.rs in
herdrdev/herdr) plus a full [theme.custom] override so the result always
matches this profile's exact palette, not just the closest built-in's
own colors. Role names below match the installed herdr version's
CustomThemeColors struct -- verified against v0.8.0 specifically, since
its `master` branch already has three more fields (sidebar_bg,
active_row_bg, selection_bg) this version doesn't recognize yet.

These per-theme role maps are hand-picked, not derived from the theme's
[palette] -- herdr wants more shades (surface0/1, overlay0/1, ...) than
the 12-key palette covers, so there's no clean formula to derive them from.
Add a new theme's block here by hand, same as the others.
"""

import re
import subprocess
from pathlib import Path

CONFIG_FILE = (
    Path(__file__).resolve().parent.parent.parent
    / "dotfiles"
    / "herdr"
    / ".config"
    / "herdr"
    / "config.toml"
)

PROFILES = {
    "gruvbox-dark": {
        "name": "gruvbox",
        "custom": {
            "accent": "#d79921",
            "panel_bg": "#282828",
            "surface0": "#3c3836",
            "surface1": "#504945",
            "surface_dim": "#665c54",
            "overlay0": "#7c6f64",
            "overlay1": "#928374",
            "text": "#ebdbb2",
            "subtext0": "#bdae93",
            "mauve": "#d3869b",
            "green": "#b8bb26",
            "yellow": "#fabd2f",
            "red": "#fb4934",
            "blue": "#83a598",
            "teal": "#8ec07c",
            "peach": "#fe8019",
        },
    },
    "catppuccin-macchiato-mauve": {
        "name": "catppuccin",
        "custom": {
            "accent": "#c6a0f6",
            "panel_bg": "#24273a",
            "surface0": "#363a4f",
            "surface1": "#494d64",
            "surface_dim": "#5b6078",
            "overlay0": "#6e738d",
            "overlay1": "#8087a2",
            "text": "#cad3f5",
            "subtext0": "#a5adcb",
            "mauve": "#c6a0f6",
            "green": "#a6da95",
            "yellow": "#eed49f",
            "red": "#ed8796",
            "blue": "#8aadf4",
            "teal": "#8bd5ca",
            "peach": "#f5a97f",
        },
    },
    "catppuccin-latte": {
        "name": "one-light",
        "custom": {
            "accent": "#8839ef",
            "panel_bg": "#eff1f5",
            "surface0": "#ccd0da",
            "surface1": "#bcc0cc",
            "surface_dim": "#acb0be",
            "overlay0": "#9ca0b0",
            "overlay1": "#8c8fa1",
            "text": "#4c4f69",
            "subtext0": "#6c6f85",
            "mauve": "#8839ef",
            "green": "#40a02b",
            "yellow": "#df8e1d",
            "red": "#d20f39",
            "blue": "#1e66f5",
            "teal": "#179299",
            "peach": "#fe640b",
        },
    },
}

# A top-level TOML section header that is NOT part of the [theme] block
# (i.e. not [theme], [theme.custom], [theme.custom.light], or
# [theme.custom.dark]) -- marks where the block being replaced ends.
_NEXT_SECTION_RE = re.compile(r"^\[(?!theme(?:\.|\]))")


def _render_theme_block(name: str, custom: dict) -> str:
    lines = ["[theme]", f'name = "{name}"', "", "[theme.custom]"]
    lines += [f'{key} = "{value}"' for key, value in custom.items()]
    return "\n".join(lines) + "\n\n"


def apply(profile: dict) -> bool:
    herdr_theme = profile.get("herdr_theme")
    if not herdr_theme:
        return False

    herdr_profile = PROFILES.get(herdr_theme)
    if herdr_profile is None:
        print(
            f"[herdr] no PROFILES entry for '{herdr_theme}' in "
            "core/theme_appliers/herdr_theme.py, skipping"
        )
        return False

    if not CONFIG_FILE.exists():
        print(f"[herdr] no config file at {CONFIG_FILE}, skipping")
        return False

    print(f"[herdr] herdr_theme={herdr_theme}")
    lines = CONFIG_FILE.read_text().splitlines(keepends=True)

    start = next((i for i, line in enumerate(lines) if line.strip() == "[theme]"), None)
    if start is None:
        print("[herdr] no [theme] section found in config.toml, skipping")
        return False

    end = len(lines)
    for i in range(start + 1, len(lines)):
        if _NEXT_SECTION_RE.match(lines[i]):
            end = i
            break

    new_block = _render_theme_block(herdr_profile["name"], herdr_profile["custom"])
    lines[start:end] = [new_block]
    CONFIG_FILE.write_text("".join(lines))

    result = subprocess.run(["herdr", "server", "reload-config"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[herdr] reload-config exited {result.returncode}: {result.stderr.strip()}")

    return True
