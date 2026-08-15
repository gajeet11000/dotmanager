import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "packages.json"

LIST_KEYS = ("official", "aur", "flatpak", "essential")


def load() -> dict:
    with open(DATA_FILE) as f:
        data = json.load(f)
    for key in LIST_KEYS:
        data.setdefault(key, [])
    return data


def save(data: dict) -> None:
    ordered = {key: sorted(set(data[key])) for key in LIST_KEYS}
    with open(DATA_FILE, "w") as f:
        json.dump(ordered, f, indent=2)
        f.write("\n")
