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

# 1. Python deps (stdlib only, but `uv sync` still sets up the .venv every
# command below assumes via `uv run`, or an activated .venv).
uv sync

# 2. Packages (pacman + AUR + Flatpak, from packages.json)
uv run python3 main.py install all          # or `essentials` for a faster subset

# 3. Symlink every dotfiles/* package into $HOME
uv run python3 main.py stow stow all
# Log out and back in (or restart Hyprland) once after this -- Hyprland only
# exports environment.lua's env vars (QT_QPA_PLATFORMTHEME, XCURSOR_THEME,
# ...) at compositor startup, so anything stowed after it was already
# running won't take effect until the next start.

# 4. One-time system setup -- run before the first `theme set` (see why below)
uv run python3 main.py setup gtk_theme       # installs themes/*/gtk/*.zip to /usr/share/themes
uv run python3 main.py setup cursor_theme    # installs the bundled cursor theme system-wide
uv run python3 main.py setup papirus_folders # installs papirus-folders + the catppuccin colored
                                       # folder icons (needed by the catppuccin theme's
                                       # icon accent -- its baked snapshot in
                                       # themes/catppuccin-macchiato-mauve/icons/ symlinks to
                                       # files this step provides, not stock Papirus)

# 5. Apply a theme (gruvbox-dark, catppuccin-macchiato-mauve, catppuccin-latte)
uv run python3 main.py theme list
uv run python3 main.py theme set catppuccin-macchiato-mauve
```

Step 4 installs files `theme set` expects to already be on disk --
`theme set` itself only *selects* among them, it doesn't install anything.
Skipping step 4 either fails outright (`setup gtk_theme`: `theme set`
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
uv run python3 main.py theme set <name>      # switch theme live, no logout needed
uv run python3 main.py stow restow <pkg>     # re-link a package after editing dotfiles/<pkg>/
uv run python3 main.py manage add <pkg>      # add a package to packages.json (name | name/aur | name/flatpak)
```

## Layout

- `dotfiles/<package>/` -- one GNU Stow package per app, mirroring `$HOME`'s
  structure under each (e.g. `dotfiles/kitty/.config/kitty/...`).
- `core/theme_manager.py` + `core/theme_appliers/*.py` -- the theme
  switcher. Plain and manual on purpose: one Python module per app, each
  reading whatever key(s) it needs out of a theme's `themes/<name>/theme.toml`
  and writing/copying the right file. No plugin system, no generic DSL.
- `themes/<name>/` -- one folder per theme. Fixed to three: `gruvbox-dark`,
  `catppuccin-macchiato-mauve`, `catppuccin-latte` -- this is the whole
  set, not a pattern meant to grow. Each holds its `theme.toml` plus one
  subfolder per app that needs an actual file (`gtk/`, `icons/`, `qt/`,
  `kitty/`, `waybar/`, `rofi/`, `swaync/`, `lsd/`).
- `core/setups/` -- one-time system setup routines (`main.py setup <name>`),
  each installing a bundled asset rather than rebuilding it from source
  (AUR `-git` packages, slow to build, for things that don't need to track
  upstream since they're already exactly what's wanted).
- `assets/` -- shared, non-per-theme material the setup routines install
  from: `cursor-themes/` (one cursor theme, used regardless of color
  theme), `kvantum/` (the base SVG + `.kvconfig` templates every theme's
  Qt build reuses), `icon-themes/` (the shared papirus-folders base
  archive), `sudoers/`.
- `scripts/` -- one-off maintenance tools, not part of the `main.py` CLI:
  `bake_icon_accents.py` (produces each theme's `icons/` snapshot,
  consumed by `setup papirus_folders` + `core/theme_appliers/icon_theme.py`)
  and `build_qt_theme.py` (produces each theme's `qt/` output). Both only
  need rerunning if something about these three themes' assets changes.
