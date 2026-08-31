"""Plugin lookup for `AppConfig(kind="plugin")` entries and for
`f"{live_push}:post"` hooks (see manager.py).

A plugin is any callable `apply(theme: Theme, app: AppConfig) -> bool`.
Two ways to register one:
  - Ship it in a pip package with a `hyprtheme.appliers` entry point (see
    this package's own pyproject.toml for the built-ins: gtk, icon, qt).
    Anyone who `pip install`s your plugin package gets it automatically.
  - Point `ThemeManager(plugin_dirs=[...])` at a local directory instead --
    every `*.py` file in it is imported and its module-level `apply`
    function registered under the file's stem. No packaging required; this
    is how dotmanager keeps its own personal appliers (herdr, claude) out
    of this general-purpose library.
"""

import importlib
import importlib.metadata
import importlib.util
from pathlib import Path
from typing import Callable

Applier = Callable[..., bool]

ENTRY_POINT_GROUP = "hyprtheme.appliers"


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, Applier] = {}

    def register(self, name: str, fn: Applier) -> None:
        self._plugins[name] = fn

    def get(self, name: str) -> Applier | None:
        return self._plugins.get(name)

    def discover_entry_points(self) -> None:
        for entry_point in importlib.metadata.entry_points(group=ENTRY_POINT_GROUP):
            self.register(entry_point.name, entry_point.load())

    def load_dir(self, directory: Path) -> None:
        for path in sorted(directory.glob("*.py")):
            if path.stem.startswith("_"):
                continue
            spec = importlib.util.spec_from_file_location(
                f"hyprtheme_plugin_{path.stem}", path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            apply = getattr(module, "apply", None)
            if apply is not None:
                self.register(path.stem, apply)
