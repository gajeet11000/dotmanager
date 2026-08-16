# AUR helper binary to use for AUR package installs.
# Change to "paru" if that's what you use.
AUR_HELPER = "yay"

# Where your stow packages live (your dotfiles repo).
STOW_DIR = "~/dotfiles"

# Where stow symlinks get placed. Normally your home dir.
TARGET_DIR = "~"

# Default mount options by filesystem type, used when adding a new fstab
# entry interactively (`setup fstab`). uid/gid=1000 assumes your normal user
# is the first non-system user account (check with `id -u` if unsure).
FSTAB_DEFAULT_OPTIONS = {
    "ntfs3": "rw,uid=1000,gid=1000,nofail,x-gvfs-show",
    "ntfs": "rw,uid=1000,gid=1000,nofail,x-gvfs-show",
    "exfat": "rw,uid=1000,gid=1000,nofail,x-gvfs-show",
    "vfat": "rw,uid=1000,gid=1000,nofail,x-gvfs-show",
}
FSTAB_DEFAULT_OPTIONS_FALLBACK = "defaults,nofail"

# SDDM astronaut theme (https://github.com/keyitdev/sddm-astronaut-theme)
SDDM_THEME_REPO = "https://github.com/keyitdev/sddm-astronaut-theme.git"
SDDM_THEME_NAME = "sddm-astronaut-theme"
SDDM_THEME_DIR = f"/usr/share/sddm/themes/{SDDM_THEME_NAME}"

# Compositor SDDM's greeter runs under when DisplayServer=wayland
SDDM_COMPOSITOR_COMMAND = "weston --shell=kiosk"
