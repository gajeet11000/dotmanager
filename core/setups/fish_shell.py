import getpass
import os
import shutil
from pathlib import Path

from config import FISH_THEME_NAME
from core import shell

# Module-level so it can be pointed elsewhere in tests.
ETC_SHELLS_PATH = "/etc/shells"


def _fish_path() -> str | None:
    return shutil.which("fish")


def _ensure_fish_in_etc_shells(fish_path: str) -> None:
    path = Path(ETC_SHELLS_PATH)
    existing = path.read_text().splitlines() if path.exists() else []
    if fish_path in existing:
        return
    print(f"Adding '{fish_path}' to {ETC_SHELLS_PATH}...")
    shell.run_with_input(["sudo", "tee", "-a", ETC_SHELLS_PATH], fish_path + "\n")


def set_default_shell() -> str | None:
    """Returns the fish path if it's (now) the default shell, else None."""
    fish_path = _fish_path()
    if not fish_path:
        print(
            "fish is not installed. Add and install it first, e.g.:\n"
            "  python3 main.py manage add fish\n"
            "  python3 main.py install essentials"
        )
        return None

    _ensure_fish_in_etc_shells(fish_path)

    user = getpass.getuser()
    current_shell = os.environ.get("SHELL", "")
    if current_shell == fish_path:
        print(f"fish is already the default shell for '{user}'.")
        return fish_path

    print(f"Changing default shell for '{user}' to {fish_path}...")
    shell.run(["sudo", "chsh", "-s", fish_path, user])
    print("Set. This applies to new terminals/sessions from now on.")
    return fish_path


def set_theme() -> None:
    fish_path = _fish_path()
    if not fish_path:
        print("fish is not installed, can't set its theme.")
        return

    theme_file = (
        Path.home() / ".config" / "fish" / "themes" / f"{FISH_THEME_NAME}.theme"
    )
    if not theme_file.exists():
        print(f"Warning: theme file not found at '{theme_file}'. Trying anyway.")

    print(f"Setting fish theme to '{FISH_THEME_NAME}'...")
    # 'theme choose' only applies colors for the current session (global scope).
    # 'theme save' is what actually persists them as universal variables — and
    # it prompts for a y/N confirmation on stdin, which we answer here.
    script = f'fish_config theme choose "{FISH_THEME_NAME}"; fish_config theme save'
    shell.run_with_input([fish_path, "-c", script], "y\n")


def _offer_exec_fish(fish_path: str) -> None:
    answer = (
        input("\nSwitch to fish right now in this terminal? [y/N] ").strip().lower()
    )
    if answer != "y":
        return
    print("Switching to fish...")
    os.execvp(fish_path, [fish_path])  # replaces this process; never returns on success


def setup() -> None:
    fish_path = set_default_shell()
    set_theme()
    if fish_path:
        _offer_exec_fish(fish_path)
