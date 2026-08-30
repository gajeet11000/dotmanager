import sys

from core import shell


def setup() -> None:
    if not shell.command_exists("nwg-look"):
        print(
            "nwg-look is not installed. Add and install it first, e.g.:\n"
            "  python3 main.py manage add nwg-look\n"
            "  python3 main.py install essentials",
            file=sys.stderr,
        )
        sys.exit(1)

    print("Applying current gsettings via nwg-look -a...")
    shell.run(["nwg-look", "-a"])

    # -a only pushes gsettings/dconf; apps that read settings.ini/gtkrc-2.0/
    # xsettingsd directly (not through the gsettings/portal path) need -x too.
    print("Exporting settings.ini / gtkrc-2.0 / xsettingsd via nwg-look -x...")
    shell.run(["nwg-look", "-x"])
