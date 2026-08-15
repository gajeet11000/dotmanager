import shutil
import subprocess
import sys


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print(f"\n$ {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    if check and result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
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
