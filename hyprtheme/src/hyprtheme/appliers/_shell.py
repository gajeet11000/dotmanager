import subprocess
import sys


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print(f"\n$ {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    if check and result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
        sys.exit(result.returncode)
    return result
