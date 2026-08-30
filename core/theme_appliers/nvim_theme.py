"""Applies a theme profile's neovim colorscheme.

Rewrites dotfiles/nvim/.config/nvim/lua/config/current-theme.lua (what a
newly-started nvim reads on startup -- see lua/config/theme.lua for the
name-to-colorscheme mapping, which is nvim-specific detail this module
doesn't need to know), then live-reloads every already-running nvim
session by calling into its RPC socket. Each session opens one of these
sockets itself on startup (see lua/config/lazy.lua), under
~/.cache/nvim/dotmanager-sockets/<pid>.sock. A socket that no longer
accepts connections belongs to a session that died without cleaning up
(normally nvim removes its own socket file on exit) -- that's treated as
stale and deleted, not an error.
"""

import subprocess
from pathlib import Path

NVIM_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "dotfiles"
    / "nvim"
    / ".config"
    / "nvim"
)
CURRENT_THEME_FILE = NVIM_DIR / "lua" / "config" / "current-theme.lua"
SOCKETS_DIR = Path.home() / ".cache" / "nvim" / "dotmanager-sockets"


def apply(profile: dict) -> bool:
    nvim_theme = profile.get("nvim_theme")
    if not nvim_theme:
        return False

    print(f"[nvim] nvim_theme={nvim_theme}")
    CURRENT_THEME_FILE.write_text(f'-- Rewritten by core/theme_appliers/nvim_theme.py on `dotmanager theme set`.\nreturn "{nvim_theme}"\n')

    if not SOCKETS_DIR.is_dir():
        return True

    expr = f'v:lua.require("config.theme").apply("{nvim_theme}")'
    live = 0
    for sock in SOCKETS_DIR.glob("*.sock"):
        result = subprocess.run(
            ["nvim", "--server", str(sock), "--remote-expr", expr],
            capture_output=True,
            timeout=5,
        )
        if result.returncode == 0:
            live += 1
        else:
            sock.unlink(missing_ok=True)

    if live:
        print(f"[nvim] live-reloaded {live} running session(s)")

    return True
