import re
import time
from pathlib import Path

from core import shell

# Module-level so paths can be pointed elsewhere in tests.
FONTS_DEST = "/usr/share/fonts"
SDDM_CONF_PATH = "/etc/sddm.conf"
SDDM_CONF_SRC = str(Path(__file__).parent / "sddm.conf")

# SDDM astronaut theme (https://github.com/keyitdev/sddm-astronaut-theme)
SDDM_THEME_REPO = "https://github.com/keyitdev/sddm-astronaut-theme.git"
SDDM_THEME_NAME = "sddm-astronaut-theme"
SDDM_THEME_DIR = f"/usr/share/sddm/themes/{SDDM_THEME_NAME}"
SDDM_STYLE = "purple_leaves"


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

    _set_style(theme_dir, SDDM_STYLE)


def _set_style(theme_dir: Path, style: str) -> None:
    metadata_path = theme_dir / "metadata.desktop"
    if not metadata_path.exists():
        print(f"No metadata.desktop found at {metadata_path}, skipping style set.")
        return

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


def install_conf() -> None:
    src = Path(SDDM_CONF_SRC)
    dest = Path(SDDM_CONF_PATH)

    if not src.exists():
        print(f"Source config '{src}' not found, skipping.")
        return

    if dest.exists():
        backup_path = dest.with_suffix(dest.suffix + f".bak.{int(time.time())}")
        print(f"'{dest}' already exists, backing up to '{backup_path}'")
        shell.run(["sudo", "cp", str(dest), str(backup_path)])

    print(f"Copying {src} -> {dest}")
    shell.run(["sudo", "cp", str(src), str(dest)])


def run_all() -> None:
    install_theme()
    install_conf()
