import os
import shutil
import subprocess
import sys


def run(
    cmd: list[str], check: bool = True, env: dict | None = None, cwd: str | None = None
) -> subprocess.CompletedProcess:
    print(f"\n$ {' '.join(cmd)}\n")
    full_env = {**os.environ, **env} if env else None
    result = subprocess.run(cmd, env=full_env, cwd=cwd)
    if check and result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
        sys.exit(result.returncode)
    return result


def run_capture(
    cmd: list[str], check: bool = True, env: dict | None = None, cwd: str | None = None
) -> subprocess.CompletedProcess:
    """Like run(), but captures stdout/stderr instead of streaming them.

    Used where we need to parse or inspect output (e.g. `rclone listremotes`,
    `bw status`) rather than just show it to the user.
    """
    full_env = {**os.environ, **env} if env else None
    result = subprocess.run(cmd, env=full_env, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    return result


def command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def group_exists(name: str) -> bool:
    result = subprocess.run(
        ["getent", "group", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return result.returncode == 0


def run_with_input(
    cmd: list[str], input_text: str, check: bool = True
) -> subprocess.CompletedProcess:
    print(f"\n$ {' '.join(cmd)}  (piping in: {input_text.strip()!r})\n")
    result = subprocess.run(cmd, input=input_text, text=True)
    if check and result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
        sys.exit(result.returncode)
    return result


def label_exists(label: str) -> bool:
    result = subprocess.run(
        ["blkid", "-L", label], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return result.returncode == 0


def user_in_group(user: str, group: str) -> bool:
    result = subprocess.run(["id", "-nG", user], stdout=subprocess.PIPE, text=True)
    return group in result.stdout.split()
