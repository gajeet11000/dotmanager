import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from config import FSTAB_DEFAULT_OPTIONS, FSTAB_DEFAULT_OPTIONS_FALLBACK
from core import shell

# Module-level so it can be pointed elsewhere in tests.
FSTAB_PATH = "/etc/fstab"

_SKIP_FSTYPES = {None, "", "swap", "squashfs", "iso9660"}


def _human_bytes(n: float | None) -> str:
    if n is None:
        return "-"
    n = float(n)
    for unit in ("B", "K", "M", "G", "T"):
        if abs(n) < 1024.0:
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}P"


def list_partitions() -> list[dict]:
    """Return real partitions (with a filesystem) from lsblk, flattened."""
    result = subprocess.run(
        [
            "lsblk",
            "-J",
            "-b",
            "-o",
            "NAME,PATH,TYPE,SIZE,FSTYPE,FSUSE%,LABEL,UUID,MOUNTPOINT",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        print(f"Failed to run lsblk: {result.stderr.strip()}", file=sys.stderr)
        return []

    data = json.loads(result.stdout)
    partitions: list[dict] = []

    def walk(devices: list[dict]) -> None:
        for dev in devices:
            if dev.get("type") == "part" and dev.get("fstype") not in _SKIP_FSTYPES:
                size = dev.get("size")
                pct_raw = dev.get("fsuse%")
                pct = None
                if pct_raw:
                    try:
                        pct = float(str(pct_raw).rstrip("%"))
                    except ValueError:
                        pct = None
                used = (
                    size * pct / 100 if (size is not None and pct is not None) else None
                )
                avail = size - used if (size is not None and used is not None) else None
                partitions.append(
                    {
                        "path": dev.get("path") or f"/dev/{dev.get('name')}",
                        "fstype": dev.get("fstype"),
                        "label": dev.get("label"),
                        "uuid": dev.get("uuid"),
                        "mountpoint": dev.get("mountpoint"),
                        "size": size,
                        "used": used,
                        "avail": avail,
                    }
                )
            if dev.get("children"):
                walk(dev["children"])

    walk(data.get("blockdevices", []))
    return partitions


def _print_partition_table(partitions: list[dict]) -> None:
    rows = []
    for i, p in enumerate(partitions, start=1):
        rows.append(
            (
                str(i),
                p["path"],
                p["fstype"] or "-",
                _human_bytes(p["size"]),
                _human_bytes(p["used"]),
                _human_bytes(p["avail"]),
                p["mountpoint"] or "(not mounted)",
                p["label"] or "-",
            )
        )

    headers = ("#", "Device", "FS", "Size", "Used", "Free", "Mounted at", "Label")
    widths = [
        max(len(h), *(len(r[i]) for r in rows)) if rows else len(h)
        for i, h in enumerate(headers)
    ]

    def fmt_row(row):
        return "  ".join(cell.ljust(w) for cell, w in zip(row, widths))

    print()
    print(fmt_row(headers))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print(fmt_row(row))
    print()


def _format_entry(uuid: str, mount_point: str, fstype: str) -> str:
    options = FSTAB_DEFAULT_OPTIONS.get(fstype, FSTAB_DEFAULT_OPTIONS_FALLBACK)
    return f"UUID={uuid} {mount_point} {fstype} {options} 0 0"


def _existing_line_for_mount(mount_point: str) -> str | None:
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


def _existing_line_for_uuid(uuid: str) -> str | None:
    path = Path(FSTAB_PATH)
    if not path.exists():
        return None
    needle = f"UUID={uuid}"
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith(needle):
            return stripped
    return None


def _backup_fstab() -> None:
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = f"{FSTAB_PATH}.bak.{ts}"
    print(f"Backing up {FSTAB_PATH} -> {backup_path}")
    shell.run(["sudo", "cp", FSTAB_PATH, backup_path])


def _add_one(partition: dict) -> None:
    if not partition.get("uuid"):
        print(
            "This partition has no UUID (unusual) — can't safely add it to fstab. Skipping."
        )
        return

    name = input("Mount point name under /mnt (e.g. 'Storage'): ").strip().strip("/")
    if not name:
        print("Empty name, skipping.")
        return
    mount_point = f"/mnt/{name}"

    existing_mount = _existing_line_for_mount(mount_point)
    existing_uuid = _existing_line_for_uuid(partition["uuid"])
    if existing_mount or existing_uuid:
        existing = existing_mount or existing_uuid
        print("fstab already has an entry involving this mount point or partition:")
        print(f"  {existing}")
        print(
            "Not touching it automatically — edit /etc/fstab by hand if you want to change it."
        )
        return

    line = _format_entry(partition["uuid"], mount_point, partition["fstype"])
    print("\nProposed fstab entry:")
    print(f"  {line}")
    confirm = input("Add this entry? [y/N] ").strip().lower()
    if confirm != "y":
        print("Skipped.")
        return

    print(f"Creating mount point '{mount_point}'...")
    shell.run(["sudo", "mkdir", "-p", mount_point])

    print("Adding fstab entry...")
    shell.run_with_input(["sudo", "tee", "-a", FSTAB_PATH], line + "\n")


def setup() -> None:
    partitions = list_partitions()
    if not partitions:
        print("No partitions with a filesystem were found.")
        return

    _backup_fstab()
    added_any = False

    while True:
        _print_partition_table(partitions)
        choice = input(
            "Select a partition number to add to fstab (or 'q' to finish): "
        ).strip()
        if choice.lower() in ("q", ""):
            break
        if not choice.isdigit() or not (1 <= int(choice) <= len(partitions)):
            print("Invalid selection.")
            continue

        _add_one(partitions[int(choice) - 1])
        added_any = True

    if added_any:
        print("\nRunning 'mount -a' to apply new entries...")
        shell.run(["sudo", "mount", "-a"], check=False)
