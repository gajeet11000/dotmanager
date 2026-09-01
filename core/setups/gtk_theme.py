import zipfile
from pathlib import Path

from core import shell

# Bundled instead of pulled from AUR: these themes don't get updates upstream,
# so there's nothing to gain from rebuilding them every time vs. just
# unzipping copies we already have. Drop a theme zip in any
# themes/<name>/gtk/ and it's picked up automatically -- see THEMING.md.
THEMES_DIR = Path(__file__).resolve().parent.parent.parent / "themes"

# System-level, matching where the AUR packages used to install these.
TARGET_DIR = Path("/usr/share/themes")


def setup() -> None:
    zips = sorted(THEMES_DIR.glob("*/gtk/*.zip"))
    if not zips:
        print(f"No theme archives found under '{THEMES_DIR}/*/gtk/'.")
        return

    shell.run(["sudo", "mkdir", "-p", str(TARGET_DIR)])

    for theme_zip in zips:
        with zipfile.ZipFile(theme_zip) as zf:
            variants = sorted({name.split("/")[0] for name in zf.namelist()})

        print(f"Extracting '{theme_zip.name}' to '{TARGET_DIR}' (sudo)...")
        shell.run(["sudo", "unzip", "-o", "-q", str(theme_zip), "-d", str(TARGET_DIR)])

        print(f"  installed {len(variants)} variant(s):")
        for v in variants:
            print(f"    {v}")
