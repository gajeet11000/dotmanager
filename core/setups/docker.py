import getpass
import sys

from core import shell


def setup() -> None:
    if not shell.command_exists("docker"):
        print(
            "docker is not installed. Add it and install first, e.g.:\n"
            "  python3 main.py manage add docker\n"
            "  python3 main.py install essentials",
            file=sys.stderr,
        )
        sys.exit(1)

    user = getpass.getuser()

    print("Enabling and starting docker.service...")
    shell.run(["sudo", "systemctl", "enable", "--now", "docker.service"])

    if shell.group_exists("docker"):
        print("docker group already exists, skipping creation.")
    else:
        print("Creating docker group...")
        shell.run(["sudo", "groupadd", "docker"])

    if shell.user_in_group(user, "docker"):
        print(f"'{user}' is already in the docker group.")
    else:
        print(f"Adding '{user}' to docker group...")
        shell.run(["sudo", "usermod", "-aG", "docker", user])
        print(
            f"\nGroup membership won't apply to your current session yet. "
            f"Log out and back in (or run 'newgrp docker') to use docker without sudo."
        )
