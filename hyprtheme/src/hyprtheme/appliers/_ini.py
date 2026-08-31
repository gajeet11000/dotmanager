from pathlib import Path


def set_key(path: Path, section: str, key: str, value: str) -> None:
    """Ensure `key=value` under `[section]` in an INI file, preserving
    everything else -- creates the file/section if either is missing."""
    header = f"[{section}]"
    lines = path.read_text().splitlines(keepends=True) if path.exists() else []

    start = next((i for i, line in enumerate(lines) if line.strip() == header), None)
    if start is None:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines += [f"\n{header}\n" if lines else f"{header}\n", f"{key}={value}\n"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(lines))
        return

    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("["):
            end = i
            break

    for i in range(start + 1, end):
        if lines[i].split("=", 1)[0].strip() == key:
            lines[i] = f"{key}={value}\n"
            path.write_text("".join(lines))
            return

    lines.insert(end, f"{key}={value}\n")
    path.write_text("".join(lines))
