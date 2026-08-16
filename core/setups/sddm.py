import configparser
import io
import re
from datetime import datetime
from pathlib import Path

from config import (
    SDDM_THEME_REPO,
    SDDM_THEME_NAME,
    SDDM_THEME_DIR,
    SDDM_COMPOSITOR_COMMAND,
)
from core import shell

# Module-level so paths can be pointed elsewhere in tests.
SDDM_CONF_PATH = "/etc/sddm.conf"
FONTS_DEST = "/usr/share/fonts"
CURSOR_SEARCH_DIRS = [
    "/usr/share/icons",
    str(Path.home() / ".local/share/icons"),
    str(Path.home() / ".icons"),
]


# ---- shared ini helpers -----------------------------------------------


def _read_ini(path: str) -> configparser.ConfigParser:
    cp = configparser.ConfigParser()
    cp.optionxform = str  # preserve key case
    p = Path(path)
    if p.exists():
        try:
            cp.read(p)
        except configparser.Error as e:
            print(f"Warning: couldn't parse existing {path} ({e}), starting fresh.")
    return cp


def _backup(path: str) -> None:
    if not Path(path).exists():
        return
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = f"{path}.bak.{ts}"
    print(f"Backing up {path} -> {backup_path}")
    shell.run(["sudo", "cp", path, backup_path])


def _write_ini_via_sudo(cp: configparser.ConfigParser, path: str) -> None:
    buf = io.StringIO()
    cp.write(buf)
    shell.run(["sudo", "mkdir", "-p", str(Path(path).parent)])
    shell.run_with_input(["sudo", "tee", path], buf.getvalue())


def _set_conf_value(path: str, section: str, key: str, value: str) -> None:
    _backup(path)
    cp = _read_ini(path)
    if section not in cp:
        cp[section] = {}
    cp[section][key] = value
    _write_ini_via_sudo(cp, path)
    print(f"Set [{section}] {key}={value} in {path}")


def _parse_env_string(s: str) -> dict:
    env = {}
    for part in s.split(","):
        part = part.strip()
        if part and "=" in part:
            k, v = part.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def _format_env_string(env: dict) -> str:
    return ",".join(f"{k}={v}" for k, v in env.items())


def _update_greeter_environment(updates: dict) -> None:
    """Merge key=value pairs into [General] GreeterEnvironment without
    clobbering any existing entries (e.g. QT_WAYLAND_SHELL_INTEGRATION)."""
    cp = _read_ini(SDDM_CONF_PATH)
    current = cp["General"].get("GreeterEnvironment", "") if "General" in cp else ""
    env = _parse_env_string(current)
    env.update(updates)
    _set_conf_value(
        SDDM_CONF_PATH, "General", "GreeterEnvironment", _format_env_string(env)
    )


# ---- 1. install theme ---------------------------------------------------


def install_theme() -> None:
    theme_dir = Path(SDDM_THEME_DIR)
    if theme_dir.exists():
        print(f"'{theme_dir}' already exists, skipping clone.")
    else:
        print(f"Cloning {SDDM_THEME_REPO} -> {theme_dir}")
        shell.run(
            [
                "sudo",
                "git",
                "clone",
                "-b",
                "master",
                "--depth",
                "1",
                SDDM_THEME_REPO,
                str(theme_dir),
            ]
        )

    fonts_src = theme_dir / "Fonts"
    if fonts_src.is_dir():
        print(f"Copying fonts from {fonts_src} -> {FONTS_DEST}")
        for entry in fonts_src.iterdir():
            shell.run(["sudo", "cp", "-r", str(entry), FONTS_DEST])
        shell.run(["sudo", "fc-cache", "-f"], check=False)
    else:
        print(f"No Fonts directory found at {fonts_src}, skipping font install.")

    _select_style(theme_dir)


def _select_style(theme_dir: Path) -> None:
    themes_dir = theme_dir / "Themes"
    metadata_path = theme_dir / "metadata.desktop"
    if not themes_dir.is_dir() or not metadata_path.exists():
        return

    styles = sorted(p.stem for p in themes_dir.glob("*.conf"))
    if not styles:
        return

    print("\nAvailable style variants:")
    for i, name in enumerate(styles, start=1):
        print(f"  {i}. {name}")

    choice = input(f"Pick a style [1-{len(styles)}] (Enter to leave as-is): ").strip()
    if not choice:
        return
    if not choice.isdigit() or not (1 <= int(choice) <= len(styles)):
        print("Invalid selection, leaving style unchanged.")
        return

    style = styles[int(choice) - 1]
    content = metadata_path.read_text()
    new_content, n = re.subn(
        r"^ConfigFile=.*$",
        f"ConfigFile=Themes/{style}.conf",
        content,
        flags=re.MULTILINE,
    )
    if n == 0:
        print(
            "Could not find a ConfigFile= line in metadata.desktop, leaving it unchanged."
        )
        return

    print(f"Setting style to '{style}'...")
    shell.run_with_input(["sudo", "tee", str(metadata_path)], new_content)


# ---- 2. set active theme -------------------------------------------------


def set_theme() -> None:
    if not Path(SDDM_THEME_DIR).exists():
        print(f"Theme not found at '{SDDM_THEME_DIR}'. Run 'setup sddm install' first.")
        return
    _set_conf_value(SDDM_CONF_PATH, "Theme", "Current", SDDM_THEME_NAME)


# ---- 3. greeter display server mode ------------------------------------------


def set_display_server() -> None:
    print("\nSDDM display server modes:")
    print(
        "  1. wayland   - greeter runs under a Wayland compositor (weston by default)."
    )
    print(
        "                 SDDM calls this 'experimental' — known bug: cursor can be invisible."
    )
    print(
        "  2. x11-user  - rootless X11 greeter. Common workaround for the invisible-cursor bug."
    )
    print("  3. x11       - legacy (root) X11 greeter.")
    choice = input("Pick a mode [1-3] (default 1): ").strip() or "1"
    modes = {"1": "wayland", "2": "x11-user", "3": "x11"}
    mode = modes.get(choice)
    if not mode:
        print("Invalid selection.")
        return

    _set_conf_value(SDDM_CONF_PATH, "General", "DisplayServer", mode)

    if mode == "wayland":
        _set_conf_value(
            SDDM_CONF_PATH, "Wayland", "CompositorCommand", SDDM_COMPOSITOR_COMMAND
        )
    else:
        print(
            f"DisplayServer set to '{mode}'. If the greeter fails to start, x11-user needs "
            "Xorg.wrap(1) configured to allow non-root Xorg — see 'man Xwrapper.config'."
        )


SYSTEM_ICONS_DIR = "/usr/share/icons"
DEFAULT_CURSOR_LINK = "/usr/share/icons/default"


# ---- 4. cursor theme -------------------------------------------------------


def _list_cursor_themes() -> list[str]:
    names: list[str] = []
    for d in CURSOR_SEARCH_DIRS:
        base = Path(d)
        if not base.is_dir():
            continue
        for entry in sorted(base.iterdir()):
            if entry.name == "default":
                continue  # the system-default pointer itself, not a real theme
            if entry.is_dir() and (
                (entry / "cursors").is_dir() or (entry / "cursor.theme").exists()
            ):
                names.append(entry.name)
    seen = set()
    unique = []
    for n in names:
        if n not in seen:
            seen.add(n)
            unique.append(n)
    return unique


def _is_system_wide(name: str) -> bool:
    return (Path(SYSTEM_ICONS_DIR) / name).is_dir()


def _find_user_local(name: str) -> Path | None:
    for d in CURSOR_SEARCH_DIRS:
        if Path(d) == Path(SYSTEM_ICONS_DIR):
            continue
        candidate = Path(d) / name
        if candidate.is_dir():
            return candidate
    return None


def _promote_to_system_wide(name: str) -> None:
    """SDDM's greeter runs as a system account and can't read into a user's
    home dir, so a cursor theme only installed under ~/.icons or
    ~/.local/share/icons is invisible to it. Copy it to /usr/share/icons/."""
    if _is_system_wide(name):
        return
    src = _find_user_local(name)
    if src is None:
        print(
            f"Warning: couldn't find '{name}' under {SYSTEM_ICONS_DIR} or your user icon dirs. "
            "SDDM's greeter may not be able to see it."
        )
        return
    print(f"'{name}' is only installed under your user profile ({src}).")
    print(
        f"Copying it to {SYSTEM_ICONS_DIR}/ so the greeter (a system account) can read it..."
    )
    shell.run(["sudo", "cp", "-r", str(src), f"{SYSTEM_ICONS_DIR}/"])


def _set_system_default_cursor(name: str) -> None:
    """Some SDDM/Qt builds ignore [Theme] CursorTheme and just use whatever
    /usr/share/icons/default points to as the system default cursor theme."""
    path = Path(DEFAULT_CURSOR_LINK)
    if path.is_symlink():
        target = None
        try:
            target = path.resolve()
        except OSError:
            pass
        print(
            f"Replacing existing symlink at {path} (-> {target}) with a real directory..."
        )
        shell.run(["sudo", "rm", str(path)])
    shell.run(["sudo", "mkdir", "-p", str(path)])
    _set_conf_value(str(path / "index.theme"), "Icon Theme", "Inherits", name)


def set_cursor_theme() -> None:
    names = _list_cursor_themes()
    name = None
    if names:
        print("\nDetected cursor themes:")
        for i, n in enumerate(names, start=1):
            tag = (
                ""
                if _is_system_wide(n)
                else "  (user-only — will be copied system-wide)"
            )
            print(f"  {i}. {n}{tag}")
        choice = input(
            f"Pick a cursor theme [1-{len(names)}], or type a name: "
        ).strip()
        if choice.isdigit() and 1 <= int(choice) <= len(names):
            name = names[int(choice) - 1]
        elif choice:
            name = choice
    else:
        name = input(
            "No cursor themes auto-detected. Type a cursor theme name: "
        ).strip()

    if not name:
        print("No selection made.")
        return

    _promote_to_system_wide(name)
    _set_conf_value(SDDM_CONF_PATH, "Theme", "CursorTheme", name)
    # SDDM's Wayland greeter (esp. with weston --shell=kiosk) often fails to
    # apply [Theme] CursorTheme on its own, leaving the cursor invisible.
    # Forcing it via env var to the greeter process is the known workaround.
    _update_greeter_environment({"XCURSOR_THEME": name})
    _set_system_default_cursor(name)


# ---- 5. cursor size ---------------------------------------------------------


def set_cursor_size() -> None:
    raw = input("Cursor size, in pixels (e.g. 24): ").strip()
    if not raw.isdigit():
        print("Invalid size.")
        return
    _set_conf_value(SDDM_CONF_PATH, "Theme", "CursorSize", raw)
    _update_greeter_environment({"XCURSOR_SIZE": raw})


# ---- 6. virtual keyboard -------------------------------------------------------


def _package_installed(pkg: str) -> bool:
    result = shell.run(["pacman", "-Qq", pkg], check=False)
    return result.returncode == 0


def set_virtual_keyboard() -> None:
    if not _package_installed("qt6-virtualkeyboard"):
        print(
            "Warning: 'qt6-virtualkeyboard' doesn't look installed. The on-screen keyboard "
            "toggle will stay a no-op without it. Add and install it with:\n"
            "  python3 main.py manage add qt6-virtualkeyboard\n"
            "  python3 main.py install essentials"
        )
    _set_conf_value(SDDM_CONF_PATH, "General", "InputMethod", "qtvirtualkeyboard")
    # As with the cursor, InputMethod= alone doesn't reliably reach the greeter
    # process's actual environment. Forcing QT_IM_MODULE directly is the
    # confirmed fix (see KDE bug D5061).
    _update_greeter_environment({"QT_IM_MODULE": "qtvirtualkeyboard"})


# ---- orchestrator ------------------------------------------------------------


def run_all() -> None:
    install_theme()
    set_theme()
    set_display_server()
    set_cursor_theme()
    set_cursor_size()
    set_virtual_keyboard()
