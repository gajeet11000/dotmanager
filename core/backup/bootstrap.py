import sys
from pathlib import Path

from config import BW_RCLONE_CONFIG_ITEM_NAME, RCLONE_CONFIG_PATH
from core import shell

from .check import check
from .env import _bw_unlocked
from .restore import restore_all
from .run import init


def bootstrap() -> None:
    """For a freshly installed machine: pulls the already-authorized rclone
    Dropbox config out of Bitwarden (so there's no OAuth/browser step),
    then inits (if needed) and restores every configured target to its
    real original location.

    Requires 'bw login' + 'export BW_SESSION=...' to have been run already
    in this shell - that's the one unavoidable manual step, since only you
    can type your master password.
    """
    if not shell.command_exists("bw"):
        print(
            "[MISSING] bitwarden-cli (bw) is not installed. Install it with:\n"
            "          python3 main.py manage add bitwarden-cli/aur\n"
            "          python3 main.py install essentials"
        )
        return

    if not _bw_unlocked():
        print(
            "Bitwarden vault isn't unlocked yet. Run:\n"
            "  bw login          (first time only on this machine)\n"
            '  export BW_SESSION="$(bw unlock --raw)"\n'
            "then re-run 'backup bootstrap'."
        )
        return

    rclone_conf_path = Path(RCLONE_CONFIG_PATH).expanduser()
    if rclone_conf_path.exists():
        print(f"[ok]   {rclone_conf_path} already exists, leaving it as-is")
    else:
        note = shell.run_capture(
            ["bw", "get", "notes", BW_RCLONE_CONFIG_ITEM_NAME], check=False
        )
        if note.returncode != 0 or not note.stdout.strip():
            print(
                f"[MISSING] No Bitwarden secure note named '{BW_RCLONE_CONFIG_ITEM_NAME}'.\n"
                f"          One-time setup: run 'rclone authorize \"dropbox\"' on any device\n"
                f"          with a browser (e.g. your phone), finish 'rclone config' on this\n"
                f"          machine, then save ~/.config/rclone/rclone.conf's contents as a\n"
                f"          Bitwarden secure note under that exact name."
            )
            return
        rclone_conf_path.parent.mkdir(parents=True, exist_ok=True)
        rclone_conf_path.write_text(note.stdout)
        rclone_conf_path.chmod(0o600)
        print(f"[ok]   restored rclone config to {rclone_conf_path}")

    if not check():
        print("\nFix the items above, then re-run 'backup bootstrap'.", file=sys.stderr)
        return

    init()

    print("\nRestoring every configured target to its original location...")
    restore_all(original=True)

    print("\nDone.")
