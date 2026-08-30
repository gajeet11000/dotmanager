#!/usr/bin/env python3
"""One-off maintenance tool -- NOT part of the `main.py` CLI.

Bakes each (accent color, icon theme) combination papirus-folders needs to
produce, fixes the known folder-videos.svg symlink-alias bug, then
snapshots the resulting places/ symlinks into assets/icon-themes/. From
then on, core.theme_appliers.icon_theme just extracts the snapshot instead
of invoking papirus-folders live -- which is slow (rebuilds
gtk-update-icon-cache for Papirus *and* every sibling variant, no flag to
opt out) and buggy (folder-videos.svg is a symlink alias to folder-video.svg
for most colors, and papirus-folders' change_color() skips anything that's
already a symlink, so "videos" never gets repointed).

Run this once whenever a new (accent, icon_theme) pair is added to a theme
profile in core/theme_manager.py's THEMES that isn't covered by COMBOS
below yet. Needs sudo -- one password prompt covers the whole run via
sudo's credential cache.
"""
import subprocess
import tarfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = REPO_ROOT / "assets" / "icon-themes"

# (accent, icon_theme) pairs to bake. Keep in sync with the icon_accent /
# icon_theme values used across THEMES in core/theme_manager.py.
COMBOS = [
    ("orange", "Papirus-Dark"),
    ("orange", "Papirus-Light"),
    ("cat-macchiato-mauve", "Papirus-Dark"),
]

PLACES_GLOB_DIRS = ["/usr/share/icons/Papirus", "/usr/share/icons/Papirus-Dark", "/usr/share/icons/Papirus-Light"]


def _fix_videos_alias(icon_theme: str) -> None:
    script = (
        'for base in /usr/share/icons/Papirus "/usr/share/icons/$1"; do '
        '  for f in "$base"/*/places/folder-video.svg; do '
        '    [ -e "$f" ] || continue; '
        '    d=$(dirname "$f"); t=$(readlink "$f"); '
        '    [ -n "$t" ] && ln -sf "$t" "$d/folder-videos.svg"; '
        '  done; '
        'done'
    )
    subprocess.run(["sudo", "bash", "-c", script, "_", icon_theme], check=True)


def _bake(accent: str, icon_theme: str) -> None:
    print(f"Baking accent='{accent}' theme='{icon_theme}'...")
    subprocess.run(["sudo", "papirus-folders", "-v", "-C", accent, "--theme", icon_theme], check=True)
    _fix_videos_alias(icon_theme)


def _snapshot(accent: str, icon_theme: str) -> Path:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    out = ASSETS_DIR / f"{accent}__{icon_theme}.tar"

    symlinks = [
        f
        for base in PLACES_GLOB_DIRS
        for f in Path(base).glob("*/places/*.svg")
        if f.is_symlink()
    ]
    print(f"  snapshotting {len(symlinks)} symlinks -> {out}")
    with tarfile.open(out, "w") as tf:
        for f in symlinks:
            tf.add(f, arcname=str(f.relative_to("/")), recursive=False)
    return out


def main() -> None:
    for accent, icon_theme in COMBOS:
        _bake(accent, icon_theme)
        _snapshot(accent, icon_theme)
    print("Done.")


if __name__ == "__main__":
    main()
