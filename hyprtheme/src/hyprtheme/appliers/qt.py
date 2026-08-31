"""Built-in plugin: switches Qt5/Qt6/KDE apps to a theme's already-built
Kvantum theme + KDE `.colors` file. No color generation here, and no
dependency on the generator. The Kvantum theme and `.colors` file are
built once, ahead of time, by the separate `hyprtheme-build` package
(`hyprtheme-build qt ...`) and committed; this plugin only ever *points*
at that pre-built output -- a symlink (created once, left alone after) and
a couple of config-key writes, nothing copied on every switch.

Three real, verified mechanisms, layered because each covers a gap the
previous one left (see the original investigation this was ported from --
dotmanager's git history has the full story):

1. Kvantum for widget/window painting -- plain QPalette gets ignored by
   KDE-Frameworks apps.
2. kdeglobals's [Icons] Theme= for icon *theme selection* -- KDE Frameworks
   apps resolve this independently of qt5ct/qt6ct's own icon_theme=.
3. The `.colors` file, pointed at by a platform theme engine that links
   KIconThemes (e.g. hyprwm/hyprqt6engine) for icon *recoloring* --
   qt5ct/qt6ct can't apply KIconEngine's ColorScheme-Text substitution at
   all, since neither links KIconThemes.

Configure in apps.toml:
    [apps.qt]
    kind = "plugin"
    plugin = "qt"
    kvantum_dir = "~/.config/Kvantum"                            # optional, this default
    generated_kvantum_dir = "~/dotfiles-assets/generated/kvantum"
    generated_colors_dir = "~/dotfiles-assets/generated/color-schemes"
    kdeglobals = "~/.config/kdeglobals"                          # optional, this default
    # Only needed if you're using a platform engine that reads a
    # color_scheme path from its own config file (e.g. hyprqt6engine):
    platform_engine_conf = "~/.config/hypr/hyprqt6engine.conf"
    platform_engine_format = "theme {{\\n    color_scheme = {color_scheme}\\n    icon_theme = {icon_theme}\\n    style = {style}\\n}}\\n"
    style = "kvantum"                                            # optional, this default
"""

from pathlib import Path

from hyprtheme.apps import AppConfig
from hyprtheme.appliers._ini import set_key
from hyprtheme.theme import Theme

DEFAULT_ENGINE_FORMAT = (
    "theme {{\n"
    "    color_scheme = {color_scheme}\n"
    "    icon_theme = {icon_theme}\n"
    "    style = {style}\n"
    "}}\n"
)


def _ensure_kvantum_symlink(generated_dir: Path, kvantum_dir: Path, theme_name: str) -> None:
    """Kvantum only discovers theme folders by name under `kvantum_dir`, so
    the folder has to physically live there -- but it never changes once
    built, so linking it once and leaving it alone is enough; no copying on
    every switch."""
    src = generated_dir / theme_name
    if not src.exists():
        raise FileNotFoundError(
            f"no built Kvantum theme at {src} -- run "
            f"`hyprtheme-build qt <theme.toml> ...` for this theme first"
        )
    kvantum_dir.mkdir(parents=True, exist_ok=True)
    dest = kvantum_dir / theme_name
    if dest.is_symlink() and dest.resolve() == src.resolve():
        return
    if dest.is_symlink() or dest.is_file():
        dest.unlink()
    elif dest.is_dir():
        raise FileExistsError(f"{dest} is a real directory, not a symlink -- remove it manually")
    dest.symlink_to(src)


def apply(theme: Theme, app: AppConfig) -> bool:
    if theme.palette is None:
        print(f"[qt] theme '{theme.name}' has no [palette], skipping")
        return False

    opts = app.options
    theme_name = f"hyprtheme-{theme.name}"
    icon_theme = theme.apps.get("icon_theme", "")
    print(f"[qt] theme={theme.name} icon_theme={icon_theme or '(unset)'}")

    kvantum_dir = Path(opts.get("kvantum_dir", "~/.config/Kvantum")).expanduser()
    generated_kvantum_dir = Path(opts["generated_kvantum_dir"]).expanduser()
    _ensure_kvantum_symlink(generated_kvantum_dir, kvantum_dir, theme_name)
    (kvantum_dir / "kvantum.kvconfig").write_text(f"[General]\ntheme={theme_name}\n")

    if icon_theme:
        kdeglobals = Path(opts.get("kdeglobals", "~/.config/kdeglobals")).expanduser()
        set_key(kdeglobals, "Icons", "Theme", icon_theme)

    generated_colors_dir = Path(opts["generated_colors_dir"]).expanduser()
    color_scheme_path = generated_colors_dir / f"{theme_name}.colors"
    if not color_scheme_path.exists():
        raise FileNotFoundError(
            f"no built .colors file at {color_scheme_path} -- run "
            f"`hyprtheme-build qt <theme.toml> ...` for this theme first"
        )

    if "platform_engine_conf" in opts:
        engine_conf = Path(opts["platform_engine_conf"]).expanduser()
        engine_conf.parent.mkdir(parents=True, exist_ok=True)
        fmt = opts.get("platform_engine_format", DEFAULT_ENGINE_FORMAT)
        engine_conf.write_text(fmt.format(
            color_scheme=color_scheme_path,
            icon_theme=icon_theme,
            style=opts.get("style", "kvantum"),
        ))

    return True
