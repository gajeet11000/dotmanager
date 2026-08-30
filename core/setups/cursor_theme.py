from pathlib import Path

from core import shell

# Bundled instead of pulled from AUR: the theme never gets updates upstream,
# so there's nothing to gain from rebuilding it every time vs. just unpacking
# the copy we already have.
CURSOR_ARCHIVE = (
    Path(__file__).resolve().parent.parent.parent
    / "assets"
    / "cursor-themes"
    / "Bibata-Rainbow-Modern.tar.gz"
)

# System-level, matching where the AUR package used to install it.
TARGET_DIR = Path("/usr/share/icons")


def setup() -> None:
    if not CURSOR_ARCHIVE.exists():
        print(f"Cursor archive not found at '{CURSOR_ARCHIVE}'.")
        return

    print(f"Extracting Bibata-Rainbow-Modern cursor theme to '{TARGET_DIR}' (sudo)...")
    shell.run(["sudo", "mkdir", "-p", str(TARGET_DIR)])
    shell.run(["sudo", "tar", "-xzf", str(CURSOR_ARCHIVE), "-C", str(TARGET_DIR)])

    print("Installed Bibata-Rainbow-Modern.")
