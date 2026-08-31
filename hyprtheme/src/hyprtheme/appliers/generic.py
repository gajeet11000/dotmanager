"""The declarative file-swap engine covering `AppConfig(kind="pointer"|"copy")` --
the common case for most apps (a colorscheme file per theme, an optional
reload signal). Ported from what were kitty_theme.py, waybar_theme.py,
rofi_theme.py, swaync_theme.py, lsd_theme.py and nvim_theme.py in
dotmanager's original core/theme_appliers/, unified into one parametrized
implementation since all six did exactly this.
"""

import subprocess
from pathlib import Path

from hyprtheme.apps import AppConfig
from hyprtheme.theme import Theme


def _resolve_source(app: AppConfig, value: str) -> Path:
    # A bare filename template (the common case: themes/<name>.conf next to
    # the target file) resolves relative to target's directory; an
    # absolute/`~`-rooted source is used as-is.
    source = Path(app.source.format(value=value)).expanduser()
    return source if source.is_absolute() else app.target.parent / source


def _reload(app: AppConfig) -> None:
    if not app.reload:
        return
    result = subprocess.run(app.reload)
    if result.returncode not in app.ok_reload_codes:
        print(f"[{app.name}] {' '.join(app.reload)} exited {result.returncode}")


def apply_pointer(theme: Theme, app: AppConfig) -> bool:
    value = theme.apps.get(app.theme_key)
    if not value:
        return False

    source = _resolve_source(app, value)
    if not source.exists():
        print(f"[{app.name}] no source file at {source}, skipping")
        return False

    print(f"[{app.name}] {app.theme_key}={value}")
    app.target.parent.mkdir(parents=True, exist_ok=True)
    app.target.write_text(app.pointer_format.format(value=value))
    _reload(app)
    return True


def apply_write(theme: Theme, app: AppConfig) -> bool:
    """No source file at all -- just renders `pointer_format` with the
    theme's value and writes it straight to `target`. For apps with no
    per-theme file of their own, just a name to record (e.g. a Neovim
    config that looks up a colorscheme by name at startup)."""
    value = theme.apps.get(app.theme_key)
    if not value:
        return False

    print(f"[{app.name}] {app.theme_key}={value}")
    app.target.parent.mkdir(parents=True, exist_ok=True)
    app.target.write_text(app.pointer_format.format(value=value))
    _reload(app)
    return True


def apply_copy(theme: Theme, app: AppConfig) -> bool:
    value = theme.apps.get(app.theme_key)
    if not value:
        return False

    source = _resolve_source(app, value)
    if not source.exists():
        print(f"[{app.name}] no source file at {source}, skipping")
        return False

    print(f"[{app.name}] {app.theme_key}={value}")
    app.target.parent.mkdir(parents=True, exist_ok=True)
    app.target.write_text(source.read_text())
    _reload(app)
    return True
