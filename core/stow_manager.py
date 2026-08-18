import shutil
from pathlib import Path

from config import STOW_DIR, TARGET_DIR
from core import shell


def _stow_dir() -> Path:
    return Path(STOW_DIR).expanduser().resolve()


def _target_dir() -> Path:
    return Path(TARGET_DIR).expanduser().resolve()


def list_packages() -> list[str]:
    stow_dir = _stow_dir()
    if not stow_dir.exists():
        return []
    return sorted(
        p.name for p in stow_dir.iterdir() if p.is_dir() and not p.name.startswith(".")
    )


def _resolve_targets(names: list[str]) -> list[str]:
    if names == ["all"]:
        return list_packages()
    return names


def _run_stow(flag: str | None, names: list[str]) -> None:
    cmd = ["stow", "--no-folding", "-d", str(_stow_dir()), "-t", str(_target_dir())]
    if flag:
        cmd.append(flag)
    cmd.extend(names)
    shell.run(cmd)


def stow_packages(names: list[str]) -> None:
    targets = _resolve_targets(names)
    if not targets:
        print("No stow packages found.")
        return
    _run_stow(None, targets)


def restow_packages(names: list[str]) -> None:
    targets = _resolve_targets(names)
    if not targets:
        print("No stow packages found.")
        return
    _run_stow("-R", targets)


def unstow_packages(names: list[str]) -> None:
    targets = _resolve_targets(names)
    if not targets:
        print("No stow packages to unstow.")
        return
    _run_stow("-D", targets)


def create_package(path: str, name: str | None = None) -> None:
    """Move an existing config into the stow dir (mirroring its path relative to
    TARGET_DIR) and stow it back into place."""
    target = Path(path).expanduser().resolve()
    if not target.exists():
        raise FileNotFoundError(f"'{target}' does not exist")

    home = _target_dir()
    try:
        rel = target.relative_to(home)
    except ValueError:
        raise ValueError(f"'{target}' is not inside target dir '{home}'")

    package_name = name or rel.name.lstrip(".")
    dest = _stow_dir() / package_name / rel

    if dest.exists():
        raise FileExistsError(f"'{dest}' already exists")

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(target), str(dest))
    print(f"Moved '{target}' -> '{dest}'")

    stow_packages([package_name])


def delete_package(name: str, force: bool = False) -> None:
    package_root = _stow_dir() / name
    if not package_root.exists():
        raise FileNotFoundError(f"No such stow package '{name}'")

    if not force:
        answer = input(
            f"This will unstow and permanently delete '{package_root}'. Continue? [y/N] "
        )
        if answer.strip().lower() != "y":
            print("Aborted.")
            return

    unstow_packages([name])
    shutil.rmtree(package_root)
    print(f"Deleted stow package '{name}'")
