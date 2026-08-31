from pathlib import Path

from hyprtheme.apps import AppConfig, load_apps
from hyprtheme.appliers import generic
from hyprtheme.registry import PluginRegistry
from hyprtheme.theme import Theme, load_themes_dir


class ThemeManager:
    """Loads an apps.toml + a directory of theme .toml files, and applies
    one theme across every app that declares support for it.

    Apps sharing the same non-empty `live_push` value (see apps.py) are
    batched: every app in the group runs first, then a
    `f"{live_push}:post"` plugin (if registered) runs once -- e.g. the
    built-in `gtk`/`icon` plugins both patch an nwg-look-managed file and
    share `live_push = "nwg-look"`, so nwg-look only re-exports once for
    both instead of twice.
    """

    def __init__(
        self, apps_path: Path, themes_dir: Path, plugin_dirs: list[Path] | None = None,
    ) -> None:
        self.apps: dict[str, AppConfig] = load_apps(apps_path)
        self.themes: dict[str, Theme] = load_themes_dir(themes_dir)
        self.registry = PluginRegistry()
        self.registry.discover_entry_points()
        for plugin_dir in plugin_dirs or []:
            self.registry.load_dir(plugin_dir)

    def list_themes(self) -> list[str]:
        return sorted(self.themes)

    def _apply_one(self, theme: Theme, app: AppConfig) -> bool:
        if app.kind == "pointer":
            return generic.apply_pointer(theme, app)
        if app.kind == "write":
            return generic.apply_write(theme, app)
        if app.kind == "copy":
            return generic.apply_copy(theme, app)
        if app.kind == "plugin":
            fn = self.registry.get(app.plugin or app.name)
            if fn is None:
                print(f"[{app.name}] no plugin registered as '{app.plugin or app.name}', skipping")
                return False
            return fn(theme, app)
        raise ValueError(f"app '{app.name}': unknown kind '{app.kind}'")

    def set_theme(self, name: str) -> None:
        theme = self.themes.get(name)
        if theme is None:
            raise ValueError(f"unknown theme '{name}'. Available: {', '.join(self.list_themes())}")

        print(f"Setting theme '{name}'...")
        ran_groups: set[str] = set()
        for app in self.apps.values():
            if app.live_push:
                if app.live_push in ran_groups:
                    continue
                for grouped in self.apps.values():
                    if grouped.live_push == app.live_push:
                        self._apply_one(theme, grouped)
                hook = self.registry.get(f"{app.live_push}:post")
                if hook is not None:
                    print(f"Applying live via '{app.live_push}' post hook...")
                    hook()
                ran_groups.add(app.live_push)
            else:
                self._apply_one(theme, app)

        print(f"Done. '{name}' is now active.")
