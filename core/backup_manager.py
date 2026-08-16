from pathlib import Path

from core import backup_store


def add_target(name: str, path: str) -> None:
    targets = backup_store.load()
    if any(t["name"] == name for t in targets):
        raise ValueError(f"a target named '{name}' already exists")

    resolved = Path(path).expanduser()
    if not resolved.exists():
        print(f"Warning: '{resolved}' doesn't exist yet. Adding it anyway.")

    targets.append({"name": name, "path": path})
    backup_store.save(targets)
    print(f"Added backup target '{name}' -> {path}")


def remove_target(name: str) -> None:
    targets = backup_store.load()
    remaining = [t for t in targets if t["name"] != name]
    if len(remaining) == len(targets):
        print(f"'{name}' not found in backup targets")
        return
    backup_store.save(remaining)
    print(f"Removed backup target '{name}'")


def list_targets() -> list[dict]:
    return backup_store.load()
