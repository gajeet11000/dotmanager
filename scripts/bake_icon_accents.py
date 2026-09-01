#!/usr/bin/env python3
"""One-off maintenance tool -- NOT part of the `main.py` CLI.

Bakes each (accent color, icon theme) combination papirus-folders needs to
produce, fixes the known folder-videos.svg symlink-alias bug, then
snapshots the resulting places/ symlinks into that theme's own
themes/<name>/icons/. From then on, core/theme_appliers/icon_theme.py
just extracts the snapshot instead of invoking papirus-folders live --
which is slow (rebuilds gtk-update-icon-cache for Papirus *and* every
sibling variant, no flag to opt out) and buggy (folder-videos.svg is a
symlink alias to folder-video.svg for most colors, and papirus-folders'
change_color() skips anything that's already a symlink, so "videos" never
gets repointed).

Covers the fixed set of themes dotmanager actually uses (gruvbox-dark,
catppuccin-macchiato-mauve, catppuccin-latte) -- COMBOS below isn't meant
to grow. Rerun this only if one of these needs re-baking (e.g. after a
papirus-icon-theme update, or a fix to the baking logic itself). Needs
sudo -- one password prompt covers the whole run via sudo's credential
cache.

Skips any combo whose output .tar already exists -- baking is the whole
point of avoiding papirus-folders' slow live run, so re-running this
script shouldn't redo work for combos nothing changed about. Pass --force
to rebake everything anyway.
"""
import argparse
import subprocess
import tarfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# (accent, icon_theme, theme name) triples to bake. Keep in sync with the
# icon_accent / icon_theme values used across themes/*/theme.toml.
COMBOS = [
    ("orange", "Papirus-Dark", "gruvbox-dark"),
    ("cat-macchiato-mauve", "Papirus-Dark", "catppuccin-macchiato-mauve"),
    ("cat-latte-mauve", "Papirus-Light", "catppuccin-latte"),
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


def _snapshot(accent: str, icon_theme: str, theme: str) -> Path:
    out = _output_path(accent, icon_theme, theme)
    out.parent.mkdir(parents=True, exist_ok=True)

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


def _output_path(accent: str, icon_theme: str, theme: str) -> Path:
    return REPO_ROOT / "themes" / theme / "icons" / f"{accent}__{icon_theme}.tar"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force", action="store_true", help="rebake combos that already have an output .tar"
    )
    args = parser.parse_args()

    for accent, icon_theme, theme in COMBOS:
        out = _output_path(accent, icon_theme, theme)
        if out.exists() and not args.force:
            print(f"Skipping accent='{accent}' theme='{icon_theme}' -- already baked at {out}")
            continue
        _bake(accent, icon_theme)
        _snapshot(accent, icon_theme, theme)
    print("Done.")


if __name__ == "__main__":
    main()
