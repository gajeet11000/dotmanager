import sys
from datetime import datetime
from pathlib import Path

from config import FSTAB_ENTRIES
from core import shell

# Module-level so it can be pointed elsewhere in tests.
FSTAB_PATH = "/etc/fstab"


def _format_entry(entry: dict) -> str:
    return (
        f"LABEL={entry['label']} {entry['mount_point']} {entry['fstype']} "
        f"{entry['options']} {entry['dump']} {entry['pass']}"
    )


def _find_existing_line(mount_point: str) -> str | None:
    path = Path(FSTAB_PATH)
    if not path.exists():
        return None
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        fields = stripped.split()
        if len(fields) >= 2 and fields[1] == mount_point:
            return stripped
    return None


def _backup_fstab() -> None:
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = f"{FSTAB_PATH}.bak.{ts}"
    print(f"Backing up {FSTAB_PATH} -> {backup_path}")
    shell.run(["sudo", "cp", FSTAB_PATH, backup_path])


def _process_entry(entry: dict) -> None:
    label = entry["label"]
    mount_point = entry["mount_point"]
    line = _format_entry(entry)

    if not shell.label_exists(label):
        print(
            f"Warning: no partition found with LABEL={label}; skipping this entry.",
            file=sys.stderr,
        )
        return

    existing = _find_existing_line(mount_point)
    if existing is not None:
        if existing == line:
            print(f"fstab already has this exact entry for {mount_point}, skipping.")
        else:
            print(f"fstab already has a DIFFERENT entry for {mount_point}:")
            print(f"  existing: {existing}")
            print(f"  new:      {line}")
            print("Not touching it automatically — edit /etc/fstab by hand if you want to change it.")
        return

    print(f"Creating mount point '{mount_point}'...")
    shell.run(["sudo", "mkdir", "-p", mount_point])

    print(f"Adding fstab entry: {line}")
    shell.run_with_input(["sudo", "tee", "-a", FSTAB_PATH], line + "\n")


def setup() -> None:
    if not FSTAB_ENTRIES:
        print("No FSTAB_ENTRIES configured in config.py.")
        return

    _backup_fstab()
    for entry in FSTAB_ENTRIES:
        _process_entry(entry)

    print("\nRunning 'mount -a' to apply new entries...")
    shell.run(["sudo", "mount", "-a"], check=False)
