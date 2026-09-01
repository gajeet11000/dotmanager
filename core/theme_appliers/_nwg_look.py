import subprocess
from pathlib import Path

# The stow-managed source nwg-look reads its "apply" state from. Editing this
# (rather than the live ~/.local/share/nwg-look/gsettings symlink target)
# keeps the repo as the source of truth.
GSETTINGS_FILE = (
    Path(__file__).resolve().parent.parent.parent
    / "dotfiles"
    / "dot_local"
    / ".local"
    / "share"
    / "nwg-look"
    / "gsettings"
)


def patch_fields(**fields: str) -> None:
    """Rewrite the given `key=value` lines in the nwg-look gsettings file.

    Doesn't apply anything live -- call apply_live() once after all the
    fields you want changed have been patched.
    """
    lines = GSETTINGS_FILE.read_text().splitlines()
    remaining = dict(fields)
    new_lines = []
    for line in lines:
        key = line.split("=", 1)[0]
        if key in remaining:
            new_lines.append(f"{key}={remaining.pop(key)}")
        else:
            new_lines.append(line)
    if remaining:
        raise ValueError(
            f"field(s) {sorted(remaining)} not found in {GSETTINGS_FILE} "
            "(nwg-look must -x export it at least once first)"
        )
    GSETTINGS_FILE.write_text("\n".join(new_lines) + "\n")


def apply_live() -> None:
    """Push the patched file into gsettings/dconf (-a) and regenerate
    settings.ini/gtkrc-2.0/xsettingsd.conf (-x). No logout needed, as long
    as GTK_THEME is never exported (see hypr/configs/environment.lua).

    nwg-look's own INFO/WARN log lines are captured rather than streamed --
    they're noisy (every gsettings key, every run) and its logger doesn't
    play well piped through a non-tty subprocess. Silent on success; on
    failure the captured output is dumped so nothing goes missing.
    """
    for cmd in (["nwg-look", "-a"], ["nwg-look", "-x"]):
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Command failed: {' '.join(cmd)}")
            print(result.stdout, end="")
            print(result.stderr, end="")
            raise SystemExit(result.returncode)
