import shutil
from pathlib import Path

# Bundled instead of pulled live from `ya pkg add` at setup time: these
# flavors don't get updates upstream (gruvbox-dark.yazi is dotmanager's own
# remix -- see its README), so there's nothing to gain from a network call
# every fresh install vs. just copying what's already here. Purely a user
# directory (~/.config/yazi/), no sudo needed -- unlike gtk_theme/cursor_theme.
FLAVORS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "yazi-flavors"

TARGET_DIR = Path.home() / ".config" / "yazi" / "flavors"


def setup() -> None:
    flavors = sorted(p for p in FLAVORS_DIR.iterdir() if p.is_dir() and p.name.endswith(".yazi"))
    if not flavors:
        print(f"No flavor packages found under '{FLAVORS_DIR}'.")
        return

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    for flavor in flavors:
        dest = TARGET_DIR / flavor.name
        print(f"Installing '{flavor.name}' to '{dest}'...")
        shutil.copytree(flavor, dest, dirs_exist_ok=True)

    print(f"Installed {len(flavors)} flavor(s).")
