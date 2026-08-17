from config import RCLONE_REMOTE
from core import shell

from .env import _bw_unlocked


def check() -> bool:
    """Prints exactly what's missing/needed before init/run will work.

    Returns True only if everything required is actually ready to go.
    """
    ok = True

    if shell.command_exists("restic"):
        print("[ok]   restic is installed")
    else:
        print(
            "[MISSING] restic is not installed. Install it with:\n"
            "          python3 main.py manage add restic\n"
            "          python3 main.py install essentials"
        )
        ok = False

    if shell.command_exists("rclone"):
        print("[ok]   rclone is installed")
        result = shell.run_capture(["rclone", "listremotes"], check=False)
        remotes = result.stdout.split()
        if f"{RCLONE_REMOTE}:" in remotes:
            print(f"[ok]   rclone remote '{RCLONE_REMOTE}' is configured")
        else:
            print(
                f"[MISSING] rclone remote '{RCLONE_REMOTE}' is not configured.\n"
                f"          Run 'python3 main.py backup bootstrap' to restore it from\n"
                f"          Bitwarden, or 'rclone config' to authorize it fresh."
            )
            ok = False
    else:
        print(
            "[MISSING] rclone is not installed. Install it with:\n"
            "          python3 main.py manage add rclone\n"
            "          python3 main.py install essentials"
        )
        ok = False

    if shell.command_exists("bw"):
        print("[ok]   bitwarden-cli (bw) is installed")
        if _bw_unlocked():
            print("[ok]   bitwarden vault is unlocked")
        else:
            print(
                "[MISSING] bitwarden vault isn't unlocked in this shell. Run:\n"
                "          bw login          (first time only on this machine)\n"
                '          export BW_SESSION="$(bw unlock --raw)"'
            )
            ok = False
    else:
        print(
            "[MISSING] bitwarden-cli (bw) is not installed. Install it with:\n"
            "          python3 main.py manage add bitwarden-cli/aur\n"
            "          python3 main.py install essentials"
        )
        ok = False

    return ok
