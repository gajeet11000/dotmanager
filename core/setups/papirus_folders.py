from pathlib import Path

from core import shell

# Bundled instead of pulled from AUR: papirus-folders-catppuccin-git is a
# "-git" package that's slow to build via makepkg despite being nothing but
# the `papirus-folders` CLI script and ~21k pre-rendered colored folder SVGs
# it merges into the base Papirus icon tree. Snapshotting that build output
# once and unzipping it is instant.
ARCHIVE = (
    Path(__file__).resolve().parent.parent.parent
    / "assets"
    / "icon-themes"
    / "papirus-folders-catppuccin.zip"
)


def setup() -> None:
    if not ARCHIVE.exists():
        print(f"Archive not found at '{ARCHIVE}'.")
        return

    if not Path("/usr/share/icons/Papirus").exists():
        print(
            "Base Papirus icon theme not found at /usr/share/icons/Papirus.\n"
            "Install it first, e.g.: sudo pacman -S --needed papirus-icon-theme"
        )
        return

    # The zip's paths are root-relative (usr/bin/..., usr/share/icons/...),
    # so it extracts straight over the existing system tree.
    print(f"Extracting papirus-folders CLI + colored folder icons to '/' (sudo)...")
    shell.run(["sudo", "unzip", "-o", "-q", str(ARCHIVE), "-d", "/"])

    print("Refreshing the icon cache...")
    shell.run(["sudo", "gtk-update-icon-cache", "-f", "/usr/share/icons/Papirus"])

    print("Installed papirus-folders. Try: papirus-folders -C cat-macchiato-mauve --theme Papirus-Dark")
