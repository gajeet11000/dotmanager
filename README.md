# dotmanager

Personal Arch Linux + Hyprland dotfiles, managed with GNU Stow and a small
Python CLI (`main.py`). Covers package installation, dotfile symlinking,
system setup steps (GTK/icon/cursor themes, SDDM, Docker, ...), and live
theme switching across GTK, Qt/KDE, the terminal stack, and Neovim.

## Fresh install

Assumes a working Arch Linux + Hyprland session already logged in (this repo
doesn't bootstrap the OS or window manager itself), and `yay` installed for
AUR packages.

```sh
git clone <this-repo> ~/Projects/dotmanager
cd ~/Projects/dotmanager

# 1. Packages (pacman + AUR + Flatpak, from packages.json)
python3 main.py install all          # or `essentials` for a faster subset

# 2. Symlink every dotfiles/* package into $HOME
python3 main.py stow stow all
# Log out and back in (or restart Hyprland) once after this -- Hyprland only
# exports environment.lua's env vars (QT_QPA_PLATFORMTHEME, XCURSOR_THEME,
# ...) at compositor startup, so anything stowed after it was already
# running won't take effect until the next start.

# 3. One-time system setup -- run before the first `theme set` (see why below)
python3 main.py setup gtk_theme       # installs assets/gtk-themes/*.zip to /usr/share/themes
python3 main.py setup cursor_theme    # installs the bundled cursor theme system-wide
python3 main.py setup papirus_folders # installs papirus-folders + the catppuccin colored
                                       # folder icons (needed by the catppuccin theme's
                                       # icon accent -- its baked snapshot in
                                       # assets/icon-themes/ symlinks to files this step
                                       # provides, not stock Papirus)

# 4. Apply a theme
python3 main.py theme list
python3 main.py theme set catppuccin-macchiato-mauve
```

Steps 3 install files `theme set` expects to already be on disk --
`theme set` itself only *selects* among them, it doesn't install anything.
Skipping step 3 either fails outright (`setup gtk_theme`: `theme set`
validates the GTK theme directory exists first) or partially breaks (skip
`setup papirus_folders` and catppuccin's icon accent extracts, but its
symlinks dangle since the files they point to were never installed).

### Optional: passwordless theme switching from a keybind

`theme set`'s icon accent step needs `sudo` (extracting a baked icon
snapshot + rebuilding the icon cache). That's fine from an interactive
terminal -- sudo just prompts -- but breaks with nothing attached to prompt,
e.g. a Hyprland keybind calling the rofi theme switcher. To allow that
specific case:

```sh
sudo install -m 0440 assets/sudoers/dotmanager-theme /etc/sudoers.d/dotmanager-theme
sudo visudo -c   # verify it parses before trusting it
```

See that file for exactly what it grants (scoped to this repo's own baked
icon archives and the two Papirus icon caches -- nothing a user who already
owns this repo's files couldn't already do).

## Everyday use

```sh
python3 main.py theme set <name>      # switch theme live, no logout needed
python3 main.py stow restow <pkg>     # re-link a package after editing dotfiles/<pkg>/
python3 main.py manage add <pkg>      # add a package to packages.json (name | name/aur | name/flatpak)
```

## Layout

- `dotfiles/<package>/` -- one GNU Stow package per app, mirroring `$HOME`'s
  structure under each (e.g. `dotfiles/kitty/.config/kitty/...`).
- `core/theme_appliers/` -- one module per app for `theme set`, each reading
  whichever keys it cares about from a profile in `core/theme_manager.py`'s
  `THEMES` and no-op'ing if none are present. See that package's own
  docstring for how to add a new app.
- `core/setups/` -- one-time system setup routines (`main.py setup <name>`),
  each installing a bundled asset rather than rebuilding it from source
  (AUR `-git` packages, slow to build, for things that don't need to track
  upstream since they're already exactly what's wanted).
- `assets/` -- bundled themes/icons/cursors/kvantum templates the setup
  routines and theme appliers install from, instead of an AUR rebuild or a
  live external tool call every time.
- `scripts/` -- one-off maintenance tools, not part of the `main.py` CLI
  (e.g. `bake_icon_accents.py`, which produces the snapshots
  `setup papirus_folders` + the icon theme applier consume).
