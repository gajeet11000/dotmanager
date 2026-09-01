# Adding a theme

Example theme used throughout: `catppuccin-latte`. Replace with your own name/values.

## 1. Create the theme folder + `theme.toml`

```sh
mkdir -p themes/catppuccin-latte
```

`themes/catppuccin-latte/theme.toml`:

```toml
name = "catppuccin-latte"

[apps]

[palette]
```

## 2. Fill in the color palette

Edit `[palette]` in `theme.toml`:

```toml
[palette]
base = "light"
bg = "#eff1f5"
fg = "#4c4f69"
accent = "#8839ef"
muted = "#6c6f85"
red = "#d20f39"
green = "#40a02b"
yellow = "#df8e1d"
blue = "#1e66f5"
purple = "#8839ef"
cyan = "#179299"
orange = "#fe640b"
selection_bg = "#ccd0da"
```

All values are hex (`#rrggbb`). `base` is `"light"` or `"dark"`.

**Used by:** `claude_theme.py` (computes ~50 Claude Code color tokens from
this live, every switch) and `scripts/build_qt_theme.py` (computes the Qt
theme once, see step 9).

## 3. GTK theme

Two ways to get the theme onto disk -- pick one.

**Option A -- install it as a package** (AUR/pacman/etc.):

```sh
yay -S catppuccin-gtk-theme-latte
```

Then list what's actually installed, and copy the exact folder name you want:

```sh
ls /usr/share/themes ~/.local/share/themes
```

**Option B -- bundle a zip in this repo** (so `setup gtk_theme` installs it
on any fresh machine too, no AUR needed). A GTK theme zip's top level must
be the theme folder(s) themselves -- unzipping it should drop straight
into `/usr/share/themes/`, no extra wrapper folder:

```
catppuccin-latte-mauve-standard+default.zip
└── catppuccin-latte-mauve-standard+default/
    ├── index.theme
    ├── gtk-3.0/
    │   ├── gtk.css
    │   ├── gtk-dark.css
    │   └── assets/
    └── gtk-4.0/
        ├── gtk.css
        └── assets/
```

```sh
mkdir -p themes/catppuccin-latte/gtk
cp ~/Downloads/catppuccin-latte-mauve-standard+default.zip themes/catppuccin-latte/gtk/theme.zip
uv run python3 main.py setup gtk_theme
```

Then confirm the exact installed folder name the same way as Option A:

```sh
ls /usr/share/themes ~/.local/share/themes
```

Add whichever exact name you got to `theme.toml`:

```toml
[apps]
gtk_theme = "catppuccin-latte-mauve-standard+default"
color_scheme = "prefer-light"
```

**Used by:** `gtk_theme.py` -- writes `gtk_theme`/`color_scheme` into the
nwg-look gsettings file, then `theme set` pushes it live via `nwg-look -a -x`.

## 4. Icon theme

Pick an installed icon theme variant:

```toml
[apps]
icon_theme = "Papirus-Light"
```

If using an accent color, bake it once (only if this exact
`(accent, icon_theme)` pair isn't baked yet):

```sh
# add to COMBOS in scripts/bake_icon_accents.py:
("mauve", "Papirus-Light", "catppuccin-latte"),
```

```sh
uv run python3 scripts/bake_icon_accents.py   # needs sudo
```

```toml
[apps]
icon_accent = "mauve"
```

**Used by:** `icon_theme.py` -- patches `icon_theme` into gsettings same as
GTK; for `icon_accent`, extracts the baked tar from
`themes/catppuccin-latte/icons/` via `sudo tar` + rebuilds the icon cache.

## 5. kitty

```sh
mkdir -p themes/catppuccin-latte/kitty
curl -o themes/catppuccin-latte/kitty/theme.conf \
  https://raw.githubusercontent.com/catppuccin/kitty/main/themes/latte.conf
```

```toml
[apps]
kitty_theme = "catppuccin-latte"
```

**Used by:** `kitty_theme.py` -- writes `include <absolute path to
theme.conf>` into `~/.config/kitty/current-theme.conf`, then
`pkill -USR1 kitty` to reload.

## 6. waybar

```sh
mkdir -p themes/catppuccin-latte/waybar
curl -o themes/catppuccin-latte/waybar/theme.css \
  https://raw.githubusercontent.com/catppuccin/waybar/main/themes/latte.css
```

```toml
[apps]
waybar_theme = "catppuccin-latte"
```

**Used by:** `waybar_theme.py` -- copies `theme.css`'s contents into
`~/.config/waybar/colors/current.css`, restarts waybar.

## 7. rofi

```sh
mkdir -p themes/catppuccin-latte/rofi
cp themes/gruvbox-dark/rofi/theme.rasi themes/catppuccin-latte/rofi/theme.rasi
# then edit the hex values inside to your palette
```

```toml
[apps]
rofi_theme = "catppuccin-latte"
```

**Used by:** `rofi_theme.py` -- copies `theme.rasi` into
`~/.config/rofi/colors/current.rasi`. No reload needed.

## 8. swaync

```sh
mkdir -p themes/catppuccin-latte/swaync
cp themes/gruvbox-dark/swaync/theme.css themes/catppuccin-latte/swaync/theme.css
# then edit the :root { --cc-bg: ...; } block to your palette
```

```toml
[apps]
swaync_theme = "catppuccin-latte"
```

**Used by:** `swaync_theme.py` -- rewrites `~/.config/swaync/style.css` to
`@import` `theme.css` by absolute file URL, then
`swaync-client --reload-css`.

## 9. lsd

```sh
mkdir -p themes/catppuccin-latte/lsd
cp themes/gruvbox-dark/lsd/theme.yaml themes/catppuccin-latte/lsd/theme.yaml
# then edit the RGB values inside to your palette
```

```toml
[apps]
lsd_theme = "catppuccin-latte"
```

**Used by:** `lsd_theme.py` -- copies `theme.yaml` into
`~/.config/lsd/colors.yaml`. No reload needed.

## 10. Neovim

Edit `dotfiles/nvim/.config/nvim/lua/config/theme.lua`:

```lua
local PROFILES = {
  ...
  ["catppuccin-latte"] = { colorscheme = "catppuccin", background = "light" },
}
```

```toml
[apps]
nvim_theme = "catppuccin-latte"
```

**Used by:** `nvim_theme.py` -- writes just the name `"catppuccin-latte"`
to `~/.config/nvim/lua/config/current-theme.lua`; nvim itself looks it up
in that Lua table at startup.

## 11. herdr

Edit `core/theme_appliers/herdr_theme.py`'s `PROFILES` dict:

```python
PROFILES = {
    ...
    "catppuccin-latte": {
        "name": "one-light",
        "custom": {
            "accent": "#8839ef",
            "panel_bg": "#eff1f5",
            "surface0": "#e6e9ef",
            "surface1": "#ccd0da",
            "surface_dim": "#bcc0cc",
            "overlay0": "#9ca0b0",
            "overlay1": "#8c8fa1",
            "text": "#4c4f69",
            "subtext0": "#6c6f85",
            "mauve": "#8839ef",
            "green": "#40a02b",
            "yellow": "#df8e1d",
            "red": "#d20f39",
            "blue": "#1e66f5",
            "teal": "#179299",
            "peach": "#fe640b",
        },
    },
}
```

```toml
[apps]
herdr_theme = "catppuccin-latte"
```

**Used by:** `herdr_theme.py` -- replaces just the `[theme]` block in
`~/.config/herdr/config.toml` with this, then runs `herdr server reload-config`.

## 12. Claude Code

Nothing to do -- already covered by step 2's `[palette]`.

```toml
[apps]
claude_theme = "catppuccin-latte"
```

**Used by:** `claude_theme.py` -- computes overrides from `[palette]` live,
writes `~/.claude/themes/dotmanager.json`, sets `theme` in
`~/.claude/settings.json`.

## 13. Qt/KDE apps

```sh
uv run python3 scripts/build_qt_theme.py
```

**Used by:** builds `themes/catppuccin-latte/qt/dotmanager-catppuccin-latte/`
(Kvantum theme) + `.../dotmanager-catppuccin-latte.colors` once, from
step 2's `[palette]`. At switch time, `qt_theme.py` just symlinks to this
pre-built output -- no key needed in `[apps]`, it always uses the theme's
own `name`.

## 14. Verify

```sh
uv run python3 main.py theme set catppuccin-latte
```

## 15. Commit

```sh
git add themes/catppuccin-latte/ \
  dotfiles/nvim/.config/nvim/lua/config/theme.lua \
  core/theme_appliers/herdr_theme.py \
  scripts/bake_icon_accents.py
git commit -m "Add catppuccin-latte theme"
```
