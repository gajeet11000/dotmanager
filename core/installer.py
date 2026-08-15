import sys

from config import AUR_HELPER
from core import shell
from core import store


def _validate_essentials(data: dict) -> None:
    all_known = set(data["official"]) | set(data["aur"]) | set(data["flatpak"])
    unknown = set(data["essential"]) - all_known
    if unknown:
        print(
            f"Warning: essential package(s) not found in OFFICIAL/AUR/FLATPAK: {', '.join(sorted(unknown))}",
            file=sys.stderr,
        )


def install_official(pkgs: list[str]) -> None:
    if not pkgs:
        return
    shell.run(["sudo", "pacman", "-S", "--needed", *pkgs])


def install_aur(pkgs: list[str]) -> None:
    if not pkgs:
        return
    shell.run([AUR_HELPER, "-S", "--needed", *pkgs])


def install_flatpak(pkgs: list[str]) -> None:
    if not pkgs:
        return
    shell.run(["flatpak", "install", "-y", "flathub", *pkgs])


def install_all() -> None:
    data = store.load()
    install_official(data["official"])
    install_aur(data["aur"])
    install_flatpak(data["flatpak"])


def install_essentials() -> None:
    data = store.load()
    _validate_essentials(data)
    essential_set = set(data["essential"])
    install_official([p for p in data["official"] if p in essential_set])
    install_aur([p for p in data["aur"] if p in essential_set])
    install_flatpak([p for p in data["flatpak"] if p in essential_set])
