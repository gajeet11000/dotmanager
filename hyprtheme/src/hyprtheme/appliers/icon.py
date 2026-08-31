"""Built-in plugin: applies a theme's icon theme (light/dark variant, via
nwg-look) and an accent color (via a pre-baked papirus-folders snapshot).

Baked snapshots sidestep calling `papirus-folders` live (slow -- rebuilds
the icon cache for every sibling variant, no flag to opt out). Bake one
with `papirus-folders -C <accent> --theme <icon_theme>`, then snapshot the
resulting `places/` symlinks into `<accent>__<icon_theme>.tar` under
`assets_dir`. Restoring one is just a tar extract + one targeted cache
rebuild -- fast enough to run synchronously, and both need root, so this
runs them under sudo (works from an interactive terminal; a NOPASSWD
sudoers rule scoped to exactly these commands is needed for it to work
from somewhere with no terminal attached, e.g. a keybind).

Configure in apps.toml:
    [apps.icon]
    kind = "plugin"
    plugin = "icon"
    live_push = "nwg-look"
    gsettings_file = "~/.local/share/nwg-look/gsettings"
    assets_dir = "~/dotfiles-assets/icon-themes"
"""

from pathlib import Path

from hyprtheme.apps import AppConfig
from hyprtheme.appliers import _nwg_look, _shell
from hyprtheme.theme import Theme


def apply(theme: Theme, app: AppConfig) -> bool:
    changed = False

    if "icon_theme" in theme.apps:
        print(f"[icon] icon-theme={theme.apps['icon_theme']}")
        gsettings_file = Path(app.options["gsettings_file"]).expanduser()
        _nwg_look.patch_fields(gsettings_file, **{"icon-theme": theme.apps["icon_theme"]})
        changed = True

    if "icon_accent" in theme.apps:
        icon_theme = theme.apps.get("icon_theme", "Papirus-Dark")
        accent = theme.apps["icon_accent"]
        assets_dir = Path(app.options["assets_dir"]).expanduser()
        archive = assets_dir / f"{accent}__{icon_theme}.tar"
        if not archive.exists():
            print(
                f"[icon] no baked snapshot for accent='{accent}' theme='{icon_theme}' "
                f"(expected {archive})."
            )
            return changed

        print(f"[icon] accent={accent} (theme={icon_theme}, from baked snapshot)")
        _shell.run(["sudo", "tar", "-xf", str(archive), "-C", "/"])
        _shell.run(["sudo", "gtk-update-icon-cache", "-qf", f"/usr/share/icons/{icon_theme}"])
        changed = True

    return changed
