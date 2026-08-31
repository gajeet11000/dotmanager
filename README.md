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

# 1. Python deps, incl. the hyprtheme library this repo's theme switching
# is built on (see hyprtheme/ below) -- uv installs it editable via the
# workspace member entry in this repo's own pyproject.toml. Every command
# below assumes `uv run`, or an activated `.venv`, for this reason.
# (hyprtheme-build, the separate theme-asset generator, is also a workspace
# member but is only needed when adding a new theme -- see below.)
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
uv run python3 main.py setup gtk_theme       # installs assets/gtk-themes/*.zip to /usr/share/themes
uv run python3 main.py setup cursor_theme    # installs the bundled cursor theme system-wide
uv run python3 main.py setup papirus_folders # installs papirus-folders + the catppuccin colored
                                       # folder icons (needed by the catppuccin theme's
                                       # icon accent -- its baked snapshot in
                                       # assets/icon-themes/ symlinks to files this step
                                       # provides, not stock Papirus)

# 5. Apply a theme
uv run python3 main.py theme list
uv run python3 main.py theme set catppuccin-macchiato-mauve
```

Step 4 installs files `theme set` expects to already be on disk --
`theme set` itself only *selects* among them, it doesn't install anything.
Skipping step 4 either fails outright (`setup gtk_theme`: hyprtheme's `gtk`
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

## Adding a new theme

No Python required. Repeat the pattern in an existing `assets/themes/*.toml`
file:

1. Pick a GTK theme and confirm it's installed (`/usr/share/themes/<name>/`
   or `~/.local/share/themes/<name>/`) -- `setup gtk_theme` installs the
   bundled ones in `assets/gtk-themes/`, or install your own separately.
2. Write `assets/themes/<name>.toml`: one `<app>_theme` line per app under
   `[apps]` (copy an existing theme file as a template), plus a `[palette]`
   table of hex colors.
3. If the theme's `icon_accent` isn't already baked, add the
   `(accent, icon_theme)` pair to `scripts/bake_icon_accents.py`'s `COMBOS`
   and run it once: `uv run python3 scripts/bake_icon_accents.py` (needs
   sudo).
4. Build the theme's Kvantum + KDE `.colors` files -- a one-time step, not
   something `theme set` redoes on every switch, using the separate
   `hyprtheme-build` package (see hyprtheme's README for why it's separate):
   ```sh
   uv run hyprtheme-build qt assets/themes/<name>.toml \
     --base-svg-dark    assets/kvantum/base-dark.svg \
     --base-svg-light   assets/kvantum/base-light.svg \
     --kvconfig-template assets/kvantum/base.kvconfig.template \
     --kvantum-out      assets/generated/kvantum \
     --colors-out       assets/generated/color-schemes
   ```
5. `uv run python3 main.py theme set <name>` to verify.
6. Commit `assets/themes/<name>.toml` together with the
   `assets/generated/kvantum/hyprtheme-<name>/` and
   `assets/generated/color-schemes/hyprtheme-<name>.colors` step 4 wrote.

To remove a theme: delete its `assets/themes/<name>.toml` and, if present,
its `assets/generated/` output.

## Layout

- `dotfiles/<package>/` -- one GNU Stow package per app, mirroring `$HOME`'s
  structure under each (e.g. `dotfiles/kitty/.config/kitty/...`).
- `hyprtheme/` -- the theme-switching engine itself: a standalone,
  independently reusable library (own `pyproject.toml`, no dependency on
  the rest of this repo) for switching GTK/Qt/terminal/bar/etc. colors live
  across any set of apps. Not dotmanager-specific -- see its own README for
  the theme/app config format and how to add or remove a theme or an app
  without touching Python. `core/theme_manager.py` is this repo's own thin
  wrapper around it, pointing it at:
    - `assets/hyprtheme-apps.toml` -- where each of *this* repo's apps'
      files live and how to reload them.
    - `assets/themes/*.toml` -- one file per theme this repo defines
      (gruvbox-dark, catppuccin-macchiato-mauve, github-light). Add/remove
      a theme by adding/removing a file here.
    - `core/theme_appliers/local_plugins/` -- support for two apps
      (herdr, Claude Code) kept out of the general-purpose library since
      they're personal/niche rather than broadly reusable.
- `hyprtheme-build/` -- a separate package from `hyprtheme` (own
  `pyproject.toml`, depends on `hyprtheme` but not the other way around):
  the one-time generator that turns a theme's `[palette]` into the Kvantum
  theme + KDE `.colors` file hyprtheme's `qt` plugin needs. Only theme
  authors need it installed; switching a theme never touches it. See its
  README, or "Adding a new theme" below.
- `core/setups/` -- one-time system setup routines (`main.py setup <name>`),
  each installing a bundled asset rather than rebuilding it from source
  (AUR `-git` packages, slow to build, for things that don't need to track
  upstream since they're already exactly what's wanted).
- `assets/` -- bundled themes/icons/cursors/kvantum templates the setup
  routines and hyprtheme install from, instead of an AUR rebuild or a live
  external tool call every time. `assets/generated/` holds the Kvantum
  themes + KDE `.colors` files `hyprtheme-build` produces (see "Adding a
  new theme" above) -- committed output, not rebuilt at switch time.
- `scripts/` -- one-off maintenance tools, not part of the `main.py` CLI
  (e.g. `bake_icon_accents.py`, which produces the snapshots
  `setup papirus_folders` + hyprtheme's `icon` plugin consume).
