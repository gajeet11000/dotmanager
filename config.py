# AUR helper binary to use for AUR package installs.
# Change to "paru" if that's what you use.
AUR_HELPER = "yay"

# Where your stow packages live (your dotfiles repo).
STOW_DIR = "~/dotfiles"

# Where stow symlinks get placed. Normally your home dir.
TARGET_DIR = "~"

# Partitions to mount at boot via /etc/fstab.
FSTAB_ENTRIES = [
    {
        "label": "Windows",
        "mount_point": "/mnt/Windows",
        "fstype": "ntfs3",
        "options": "rw,uid=1000,gid=1000,nofail,x-gvfs-show",
        "dump": 0,
        "pass": 0,
    },
    {
        "label": "Storage",
        "mount_point": "/mnt/Storage",
        "fstype": "ntfs3",
        "options": "rw,uid=1000,gid=1000,nofail,x-gvfs-show",
        "dump": 0,
        "pass": 0,
    },
]
