"""Applies a theme profile's neovim colorscheme.

Rewrites dotfiles/nvim/.config/nvim/lua/config/current-theme.lua -- what
nvim reads on startup (see lua/config/lazy.lua) to pick a colorscheme via
lua/config/theme.lua's name-to-colorscheme mapping, which is nvim-specific
detail this module doesn't need to know.

Like Hyprland's own hyprland.lua, this is read once at startup, matching
how Omarchy (github.com/omacom/omarchy) handles it too -- their own
theming docs say Neovim loads its theme file at startup, and their
theme-set command's restart list pointedly excludes Neovim. An
already-open nvim session won't pick up a switch; reopen it to get the
new theme.
"""

from pathlib import Path

CURRENT_THEME_FILE = (
    Path(__file__).resolve().parent.parent.parent
    / "dotfiles"
    / "nvim"
    / ".config"
    / "nvim"
    / "lua"
    / "config"
    / "current-theme.lua"
)


def apply(profile: dict) -> bool:
    nvim_theme = profile.get("nvim_theme")
    if not nvim_theme:
        return False

    print(f"[nvim] nvim_theme={nvim_theme}")
    CURRENT_THEME_FILE.write_text(
        "-- Rewritten by core/theme_appliers/nvim_theme.py on `dotmanager theme set`.\n"
        f'return "{nvim_theme}"\n'
    )

    return True
