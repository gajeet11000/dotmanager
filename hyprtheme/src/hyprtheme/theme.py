"""A theme: a name, a set of per-app string values, and an optional raw hex
palette (only plugins that generate colors -- rather than just pointing at a
pre-made theme file -- need the palette; e.g. the built-in `qt` applier)."""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Theme:
    name: str
    apps: dict[str, str] = field(default_factory=dict)
    palette: dict[str, str] | None = None


def load_theme(path: Path) -> Theme:
    data = tomllib.loads(path.read_text())
    name = data.get("name", path.stem)
    return Theme(name=name, apps=data.get("apps", {}), palette=data.get("palette"))


def load_themes_dir(directory: Path) -> dict[str, Theme]:
    """Every `*.toml` file in `directory` is one theme -- add a theme by
    dropping a file here, remove one by deleting it. No code involved."""
    themes = {}
    for path in sorted(directory.glob("*.toml")):
        theme = load_theme(path)
        themes[theme.name] = theme
    return themes
