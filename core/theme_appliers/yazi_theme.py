"""Applies a theme profile's yazi (terminal file manager) flavor.

Yazi's own theming mechanism is "flavors" -- a folder under
~/.config/yazi/flavors/<name>.yazi/ (flavor.toml + tmtheme.xml for
code-preview syntax highlighting), installed once via `setup yazi_theme`
(see core/setups/yazi_theme.py; the flavor packages themselves live in
assets/yazi-flavors/, not per dotmanager theme -- they're static reference
material, just picked by name). At switch time this module only ever
writes which flavor name to activate, into ~/.config/yazi/theme.toml's
`[flavor]` table -- `dark`/`light` are both set to the same name to pin
one flavor regardless of Yazi's own terminal dark/light detection, per
https://yazi-rs.github.io/docs/flavors/overview.

theme.toml is written straight to the live ~/.config/yazi/ -- it's not
part of dotfiles/yazi/'s stow package, so switching a theme never touches
anything git-tracked (see _livefile.py).
"""

from pathlib import Path

from core.theme_appliers import _livefile

CURRENT_THEME_FILE = Path.home() / ".config" / "yazi" / "theme.toml"
FLAVORS_DIR = Path.home() / ".config" / "yazi" / "flavors"


def apply(profile: dict) -> bool:
    yazi_theme = profile.get("yazi_theme")
    if not yazi_theme:
        return False

    flavor_dir = FLAVORS_DIR / f"{yazi_theme}.yazi"
    if not flavor_dir.exists():
        print(
            f"[yazi] no flavor installed at {flavor_dir} -- run "
            "`python3 main.py setup yazi_theme` first, skipping"
        )
        return False

    print(f"[yazi] yazi_theme={yazi_theme}")
    _livefile.write(
        CURRENT_THEME_FILE,
        "# Rewritten by core/theme_appliers/yazi_theme.py on `dotmanager theme set`.\n"
        "[flavor]\n"
        f'dark = "{yazi_theme}"\n'
        f'light = "{yazi_theme}"\n',
    )

    return True
