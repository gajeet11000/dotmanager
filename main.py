#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# If click is not present in the current environment, re-exec with the project .venv if available
try:
    import click  # noqa: F401
except ModuleNotFoundError:
    venv_python = Path(__file__).resolve().parent / ".venv" / "bin" / "python"
    if venv_python.exists() and Path(sys.executable).resolve() != venv_python.resolve():
        os.execv(str(venv_python), [str(venv_python), *sys.argv])
    raise

from cli import cli


def main() -> None:
    cli(prog_name="dotmanager")


if __name__ == "__main__":
    main()
