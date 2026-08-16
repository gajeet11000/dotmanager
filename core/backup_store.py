import json
from pathlib import Path

from config import BACKUP_TARGETS_FILE

DATA_FILE = Path(__file__).resolve().parent.parent / BACKUP_TARGETS_FILE


def load() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE) as f:
        return json.load(f)


def save(targets: list[dict]) -> None:
    ordered = sorted(targets, key=lambda t: t["name"])
    with open(DATA_FILE, "w") as f:
        json.dump(ordered, f, indent=2)
        f.write("\n")
