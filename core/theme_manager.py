from pathlib import Path

from core import shell

REPO_ROOT = Path(__file__).resolve().parent.parent

# Where GTK themes can live; system-level (what `setup gtk_theme` installs
# into) checked first, user-level as a fallback.
THEME_SEARCH_DIRS = [Path("/usr/share/themes"), Path.home() / ".local" / "share" / "themes"]

# The stow-managed source nwg-look reads its "apply" state from. Editing this
# (rather than the live ~/.local/share/nwg-look/gsettings symlink target)
# keeps the repo as the source of truth.
NWG_GSETTINGS_FILE = (
    REPO_ROOT
    / "dotfiles"
    / "dot_local"
    / ".local"
    / "share"
    / "nwg-look"
    / "gsettings"
)


def list_installed() -> list[str]:
    names = set()
    for d in THEME_SEARCH_DIRS:
        if not d.exists():
            continue
        for entry in d.iterdir():
            if entry.is_dir() and (entry / "index.theme").exists():
                names.add(entry.name)
    return sorted(names)


def _theme_exists(name: str) -> bool:
    return any((d / name / "index.theme").exists() for d in THEME_SEARCH_DIRS)


def set_theme(name: str) -> None:
    if not _theme_exists(name):
        raise ValueError(
            f"theme '{name}' not found in {' or '.join(str(d) for d in THEME_SEARCH_DIRS)}. "
            "Run 'python3 main.py theme list' to see installed themes."
        )

    lines = NWG_GSETTINGS_FILE.read_text().splitlines()
    new_lines, found = [], False
    for line in lines:
        if line.startswith("gtk-theme="):
            new_lines.append(f"gtk-theme={name}")
            found = True
        else:
            new_lines.append(line)
    if not found:
        raise ValueError(f"no 'gtk-theme=' line found in {NWG_GSETTINGS_FILE}")
    NWG_GSETTINGS_FILE.write_text("\n".join(new_lines) + "\n")
    print(f"Set gtk-theme to '{name}' in {NWG_GSETTINGS_FILE}")

    # -a pushes it into gsettings/dconf (this is what already-running GTK3/4
    # apps live-reload from); -x regenerates settings.ini/gtkrc-2.0/
    # xsettingsd.conf so freshly-launched and non-portal-aware apps see it
    # too. No logout needed, as long as GTK_THEME is never exported.
    print("Applying live via nwg-look -a -x...")
    shell.run(["nwg-look", "-a"])
    shell.run(["nwg-look", "-x"])
    print(f"Done. '{name}' is now active.")
