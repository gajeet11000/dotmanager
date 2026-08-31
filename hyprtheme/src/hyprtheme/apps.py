"""Per-installation app configuration: where each app's files live and how
to reload it. This is what makes the library reusable -- themes only ever
say *what* value an app should get (see theme.py); apps.toml says *where*
that value goes and *how* to apply it, once, for your own dotfiles layout.

Four `kind`s:
  - "pointer": write a one-line include/import statement into `target`
    that points at `source` (formatted with the theme's value for
    `theme_key`). For config formats with an include mechanism (kitty,
    swaync's `@import`).
  - "copy": overwrite `target` with the full contents of `source`. For
    formats with no include mechanism (waybar, rofi, lsd).
  - "write": render `pointer_format` with the theme's value and write it
    straight to `target` -- no source file at all. For apps with no
    per-theme file of their own, just a name to record.
  - "plugin": hand off to a registered Python callable instead (see
    registry.py) -- for anything that needs real logic: generating colors
    from a raw palette, surgically editing one section of a larger config,
    batching a shared live-reload step. `options` is passed through
    verbatim as that plugin's config.

"pointer", "copy" and "write" all run `reload` (if set) as a subprocess
after writing -- `ok_reload_codes` lists exit codes that mean "nothing was
running to reload, that's fine" (not just 0).
"""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AppConfig:
    name: str
    kind: str  # "pointer" | "copy" | "plugin"
    theme_key: str | None = None
    target: Path | None = None
    source: str | None = None  # "{value}"-templated path, kind in (pointer, copy)
    pointer_format: str | None = None  # "{value}"-templated content, kind=pointer
    reload: list[str] | None = None
    ok_reload_codes: tuple[int, ...] = (0,)
    plugin: str | None = None  # registry name, kind=plugin
    live_push: str | None = None  # see manager.py: apps sharing a live_push
    # value get batched, then a f"{live_push}:post" plugin runs once
    options: dict = field(default_factory=dict)


def _expand(path_str: str) -> Path:
    return Path(path_str).expanduser()


def load_apps(path: Path) -> dict[str, AppConfig]:
    data = tomllib.loads(path.read_text())
    apps = {}
    for name, raw in data.get("apps", {}).items():
        known = {
            "kind", "theme_key", "target", "source", "pointer_format",
            "reload", "ok_reload_codes", "plugin", "live_push",
        }
        apps[name] = AppConfig(
            name=name,
            kind=raw["kind"],
            theme_key=raw.get("theme_key"),
            target=_expand(raw["target"]) if "target" in raw else None,
            source=raw.get("source"),
            pointer_format=raw.get("pointer_format"),
            reload=raw.get("reload"),
            ok_reload_codes=tuple(raw.get("ok_reload_codes", [0])),
            plugin=raw.get("plugin"),
            live_push=raw.get("live_push"),
            options={k: v for k, v in raw.items() if k not in known},
        )
    return apps
