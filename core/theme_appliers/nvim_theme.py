"""Applies a theme profile's neovim colorscheme.

Rewrites ~/.config/nvim/lua/config/current-theme.lua -- what nvim reads on
startup (see lua/config/lazy.lua) to pick a colorscheme via
lua/config/theme.lua's name-to-colorscheme mapping, which is nvim-specific
detail this module doesn't need to know.

Like Hyprland's own hyprland.lua, this is read once at startup, matching
how Omarchy (github.com/omacom/omarchy) handles it too -- their own
theming docs say Neovim loads its theme file at startup, and their
theme-set command's restart list pointedly excludes Neovim. An
already-open nvim session won't pick up a switch; reopen it to get the
new theme.

current-theme.lua is written straight to the live
~/.config/nvim/lua/config/ -- it's not part of dotfiles/nvim/'s stow
package, so switching a theme never touches anything git-tracked (see
_livefile.py).
"""

from pathlib import Path

from core.theme_appliers import _livefile

CURRENT_THEME_FILE = Path.home() / ".config" / "nvim" / "lua" / "config" / "current-theme.lua"


def apply(profile: dict) -> bool:
    nvim_theme = profile.get("nvim_theme")
    if not nvim_theme:
        return False

    print(f"[nvim] nvim_theme={nvim_theme}")
    _livefile.write(
        CURRENT_THEME_FILE,
        "-- Rewritten by core/theme_appliers/nvim_theme.py on `dotmanager theme set`.\n"
        f'return "{nvim_theme}"\n',
    )

    return True
