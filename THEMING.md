# Theming dotmanager, app by app

This is a walkthrough, not a reference doc. It follows one real theme --
**Catppuccin Latte**, a light theme -- from nothing to `theme set
catppuccin-latte` working, touching every app dotmanager themes along the
way. By the end you'll have added a theme yourself and understand exactly
what each of the eleven files you touched actually does.

There's no framework here to learn. `theme set <name>` runs eleven small,
independent Python functions (`core/theme_appliers/*.py`), one per app. Each
one reads whichever key(s) it cares about out of `themes/<name>/theme.toml`
and does the one thing that app needs -- write a file, patch a config key,
restart a process. Adding a theme means creating one folder,
`themes/<name>/`, and feeding all eleven the values (or files) they want.
Nothing here is generic or pluggable on purpose: if you open any of these
files, what you see is what runs.

## The layout

Every theme is one folder under `themes/`, holding its own `theme.toml`
plus one subfolder per app that needs an actual file (not every app does --
more below):

```
themes/catppuccin-latte/
  theme.toml
  gtk/theme.zip            (optional -- only if you bundle the zip, see Step 1)
  icons/mauve__Papirus-Light.tar
  qt/dotmanager-catppuccin-latte/          (Kvantum theme, generated)
  qt/dotmanager-catppuccin-latte.colors    (generated)
  kitty/theme.conf
  waybar/theme.css
  rofi/theme.rasi
  swaync/theme.css
  lsd/theme.yaml
```

Nothing here is derived from the theme's name by string-splitting -- the
folder `themes/catppuccin-latte/` *is* the theme's identity, full stop.
Every script and applier below takes that folder as a starting point and
reads/writes fixed filenames inside it.

## The map

| App | Reads | Applier | What it actually does |
| --- | --- | --- | --- |
| GTK apps | `gtk_theme`, `color_scheme` | `gtk_theme.py` | Patches two fields in the nwg-look-managed gsettings file, pushed live via `nwg-look -a -x` |
| Icon theme | `icon_theme`, `icon_accent` | `icon_theme.py` | Same gsettings file for the variant; a pre-baked tar snapshot (`icons/`) for the accent color |
| Qt/KDE apps | (the theme's own name) | `qt_theme.py` | Symlinks to a pre-built Kvantum theme + `.colors` file (`qt/`), sets two config keys |
| kitty | `kitty_theme` | `kitty_theme.py` | Rewrites a one-line `include` pointer (absolute path into `kitty/`), signals running kitty instances |
| waybar | `waybar_theme` | `waybar_theme.py` | Copies `waybar/theme.css` over the live CSS file, restarts the waybar process |
| rofi | `rofi_theme` | `rofi_theme.py` | Copies `rofi/theme.rasi` over the live color file (rofi re-reads on every launch, no reload needed) |
| swaync | `swaync_theme` | `swaync_theme.py` | Rewrites an `@import` pointer (absolute `file://` URL into `swaync/`), reloads via `swaync-client` |
| lsd | `lsd_theme` | `lsd_theme.py` | Copies `lsd/theme.yaml` over the live color file (re-read on every `lsd` invocation) |
| Neovim | `nvim_theme` | `nvim_theme.py` | Writes the theme's name to a file nvim reads at startup -- no per-theme file/folder |
| herdr | `herdr_theme` | `herdr_theme.py` | Surgically replaces the `[theme]` block in herdr's own config.toml -- no per-theme file/folder |
| Claude Code | `claude_theme`, `[palette]` | `claude_theme.py` | Computes ~50 color tokens from the raw palette, writes a theme JSON -- no per-theme file/folder |

Eight of these read a plain file out of the theme's own folder. Neovim,
herdr, and Claude Code don't -- nvim just gets a name (resolved to a
colorscheme by a Lua table), herdr's colors are hand-picked Python, and
Claude Code computes its colors live from `[palette]`. Qt also computes
from `[palette]`, but as a **one-time build step**, not at switch time --
more in Step 11.

## Step 0: pick the colors

Everything downstream comes from one set of hex values. Catppuccin publishes
Latte's officially, so this step is just transcription -- for a theme you're
inventing yourself, this is where you'd actually choose colors.

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

Only `claude_theme.py` and `scripts/build_qt_theme.py` (Qt's build step,
more below) read this table. Every other applier below uses a pre-made file
instead -- keep reading, the palette comes back into play at the very end.

Don't write the actual `themes/catppuccin-latte/theme.toml` file yet --
building it up alongside each step below makes it easier to see which piece
feeds which app. Go ahead and create the empty folder now, though:

```sh
mkdir -p themes/catppuccin-latte
```

## Step 1: GTK theme

`gtk_theme.py` doesn't generate anything -- it just tells nwg-look which
*installed* theme name to switch to, so the theme has to actually exist on
disk first, under `/usr/share/themes/<name>/` or
`~/.local/share/themes/<name>/`.

Install one (AUR has `catppuccin-gtk-theme-latte`, or grab a release from
[catppuccin/gtk](https://github.com/catppuccin/gtk)), then note its *exact*
folder name -- this is what goes in the theme file, verbatim:

```
~/.local/share/themes/catppuccin-latte-mauve-standard+default/
```

`theme_manager.py` checks this folder exists before applying anything --
skip this step and `theme set` fails outright with a clear error, rather
than silently applying a broken theme.

If you'd rather bundle the theme's zip in this repo instead of relying on
AUR (so `setup gtk_theme` installs it on any fresh machine -- see the three
existing themes for the pattern), drop it at
`themes/catppuccin-latte/gtk/theme.zip`. `setup gtk_theme` globs
`themes/*/gtk/*.zip` and installs every one it finds, so nothing else needs
to know about it.

## Step 2: icon theme

Two independent things live under "icon theme": which variant (light/dark)
and an accent color for folder icons.

**Variant**: pick one that ships a light build -- Papirus does
(`Papirus-Light`, from the `papirus-icon-theme` package).

**Accent**: `icon_theme.py` never calls `papirus-folders` live (it's slow --
rebuilds the icon cache for every color variant, not just the one you
picked). Instead it extracts a pre-baked snapshot from
`themes/<name>/icons/<accent>__<icon_theme>.tar` -- Catppuccin Latte's
would be `themes/catppuccin-latte/icons/mauve__Papirus-Light.tar`. If the
`(accent, icon_theme)` pair you want isn't baked yet, add it (with the
theme name) to `COMBOS` in `scripts/bake_icon_accents.py` and run that
once:

```sh
uv run python3 scripts/bake_icon_accents.py   # needs sudo
```

For Catppuccin Latte, say you want `mauve` as the accent:

```python
COMBOS = [
    ("orange", "Papirus-Dark", "gruvbox-dark"),
    ("cat-macchiato-mauve", "Papirus-Dark", "catppuccin-macchiato-mauve"),
    ("blue", "Papirus-Light", "github-light"),
    ("mauve", "Papirus-Light", "catppuccin-latte"),   # new
]
```

## Step 3: kitty

`kitty_theme.py` writes a one-line pointer to kitty's `current-theme.conf`
(`include <absolute path>`), pointing at `themes/<name>/kitty/theme.conf`.
Catppuccin ships a ready-made kitty config -- grab
[catppuccin/kitty's `latte.conf`](https://github.com/catppuccin/kitty) and
save it as:

```
themes/catppuccin-latte/kitty/theme.conf
```

## Step 4: waybar

Same shape, different mechanism: `waybar_theme.py` doesn't write a pointer,
it copies `waybar/theme.css`'s contents over the live CSS file outright
(CSS's `@import` works, but waybar's own change-detection only watches
`style.css` itself, so a full restart happens anyway -- see the module's
docstring for why). Catppuccin ships one for waybar too --
[catppuccin/waybar's `latte.css`](https://github.com/catppuccin/waybar) --
save it as:

```
themes/catppuccin-latte/waybar/theme.css
```

If you're inventing your own theme rather than using Catppuccin's, copy an
existing theme's `waybar/theme.css` and re-map its named roles (`mauve`,
`flamingo`, ...) to your own palette -- the role names are just what
`style.css`'s existing rules already reference, not anything special.

## Step 5: rofi

`rofi_theme.py` copies `rofi/theme.rasi` over the live color file, which
both `application_launcher.rasi` and `window_switcher.rasi` `@import`. No
official Catppuccin rofi colors ship in the same repo shape as kitty/waybar,
so copy an existing theme's file and re-map colors, same as waybar above:

```
themes/catppuccin-latte/rofi/theme.rasi
```

Only `base`, `text`, `mauve`, `red`, `overlay0`, `blue`, `flamingo` are
actually referenced by the two `.rasi` files that import this -- the rest
exist for consistency with the other apps' role names, not because rofi
needs them.

## Step 6: swaync

`swaync_theme.py` rewrites `style.css` to `@import` the theme's
`swaync/theme.css` by absolute `file://` URL, then reloads live via
`swaync-client --reload-css`. Each theme file imports the packaged base
stylesheet first (for layout), then overrides just the color variables:

```
themes/catppuccin-latte/swaync/theme.css
```

Copy an existing one and edit its `:root { --cc-bg: ...; }` block with your
palette's RGB triples.

## Step 7: lsd

`lsd_theme.py` copies `lsd/theme.yaml` over the live `colors.yaml` outright
-- lsd re-reads its config on every invocation, so no reload step exists.
lsd only lets you theme
user/group/permission/attributes/date/size/inode/links/git-status; file-type
colors (directory, symlink, ...) are hardcoded upstream and can't be
touched here.

```
themes/catppuccin-latte/lsd/theme.yaml
```

## Step 8: Neovim

This is the first app that has no per-theme file at all. `nvim_theme.py`
writes *only the theme's name* to `current-theme.lua` -- nvim itself
resolves that name to an actual colorscheme plugin, via a table in
`dotfiles/nvim/.config/nvim/lua/config/theme.lua`:

```lua
local PROFILES = {
  ["gruvbox-dark"] = { colorscheme = "gruvbox", background = "dark" },
  ["catppuccin-macchiato-mauve"] = { colorscheme = "catppuccin", background = "dark" },
  ["github-light"] = { colorscheme = "vscode", background = "light" },
}
```

Add an entry for the new theme, pointing at whatever colorscheme plugin you
have installed (Catppuccin ships its own `catppuccin.nvim`, which reads
`vim.g.catppuccin_flavour` itself for the light/dark variant, so this can
reuse the same `"catppuccin"` colorscheme name the macchiato entry uses):

```lua
["catppuccin-latte"] = { colorscheme = "catppuccin", background = "light" },
```

An already-open nvim session won't pick this up -- like Hyprland's own
config, it's read once at startup; reopen it after switching.

## Step 9: herdr

Also no per-theme file. herdr's `config.toml` holds keybindings and other
settings alongside theme, so `herdr_theme.py` can't blanket-overwrite the
file -- it surgically replaces just the `[theme]` block. The actual color
values live in a `PROFILES` dict inside `herdr_theme.py` itself, not under
`themes/`, because herdr wants more shades (surface0/1, overlay0/1, ...)
than the 12-key palette covers -- there's no clean formula from
`bg`/`fg`/`accent` to herdr's exact roles, so each theme gets a hand-picked
block:

```python
PROFILES = {
    ...
    "catppuccin-latte": {
        "name": "one-light",   # closest built-in herdr theme, as a fallback base
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

(The role names above -- `panel_bg`, `surface0`, `overlay0`, ... -- come
from herdr's own `CustomThemeColors` struct; Catppuccin's own published
Latte palette happens to name most of the equivalent shades already, so
this is mostly transcription for an official Catppuccin flavor. For a fully
invented theme, derive them by eye from your `bg`/`fg`, same idea as
`build_qt_theme.py` does mechanically for Qt -- see Step 11.)

This is the one place adding a theme touches hand-picked Python instead of
just a file -- unavoidable given herdr needs more shades than the palette
carries.

## Step 10: Claude Code (this tool)

Nothing to do here. `claude_theme.py` reads the theme's `[palette]` table
directly and computes every token (including shimmer/diff/subagent
variants) via simple hex mixing -- see the function `_build_overrides()` in
that file if you want to see exactly how. As long as Step 0's `[palette]`
table is present in the theme file, this one just works.

## Step 11: Qt/KDE apps

The other palette-driven app, but unlike Claude Code, this one's output
(a Kvantum theme + a KDE `.colors` file) is **built once, ahead of time**,
not computed on every `theme set`. A theme's palette never changes at
runtime, so there's nothing to gain by recomputing it on every switch --
`scripts/build_qt_theme.py` renders it once into the theme's own `qt/`
folder, and `qt_theme.py` just symlinks to that output at switch time.
(The same idea as Step 2's icon-accent baking -- compute once, apply
cheaply forever.)

Once your theme file has a `[palette]` table (Step 0), regenerate every
theme's Qt assets:

```sh
uv run python3 scripts/build_qt_theme.py
```

This writes `themes/catppuccin-latte/qt/dotmanager-catppuccin-latte/` (the
Kvantum theme) and `themes/catppuccin-latte/qt/dotmanager-catppuccin-latte.colors`.
**Commit both** -- they're build output, checked in like any other asset,
not regenerated at switch time. It's always safe to rerun this script any
time; it fully regenerates every theme's `qt/` output from scratch.

If you're curious how the palette becomes Kvantum's window/button/text
colors or the `.colors` file's `[Colors:*]` sections, read
`build_tokens()` and `_colors_file()` in that script directly -- it's about
80 lines of straightforward hex math, no abstraction to look through.

## Step 12: write the theme file

Everything above produces either a file on disk or an entry in some Python
dict. The last piece ties them together -- every `themes/<name>/`
subfolder is `theme_manager.py`'s glob (`themes/*/theme.toml`), no
registration step:

```toml
# themes/catppuccin-latte/theme.toml
name = "catppuccin-latte"

[apps]
gtk_theme = "catppuccin-latte-mauve-standard+default"
color_scheme = "prefer-light"
icon_theme = "Papirus-Light"
icon_accent = "mauve"
kitty_theme = "catppuccin-latte"
waybar_theme = "catppuccin-latte"
rofi_theme = "catppuccin-latte"
swaync_theme = "catppuccin-latte"
lsd_theme = "catppuccin-latte"
nvim_theme = "catppuccin-latte"
herdr_theme = "catppuccin-latte"
claude_theme = "catppuccin-latte"

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

Every `<app>_theme` value under `[apps]` is a fixed value each applier
looks for -- `gtk_theme` is the exact installed folder name from Step 1,
`icon_theme`/`icon_accent` are Step 2's values, and the rest
(kitty/waybar/rofi/swaync/lsd/nvim/herdr/claude) all just repeat the
theme's own name, since that's what those appliers use to find their
per-app subfolder (or, for nvim/herdr/claude, the dict entry). Qt has no
key of its own -- `qt_theme.py` always uses the theme's own top-level
`name` too, since `theme_dir` (the `themes/<name>/` folder itself) already
tells every applier exactly where to look.

Any app you leave out of `[apps]` is just skipped for this theme -- nothing
breaks, no error. That's also how you'd theme only *some* apps for a quick
one-off theme, rather than every one of the eleven.

## Step 13: verify

```sh
uv run python3 main.py theme list
# catppuccin-latte
# ...

uv run python3 main.py theme set catppuccin-latte
```

Watch the output -- each applier prints one line when it runs (`[kitty]
kitty_theme=catppuccin-latte`, etc.) and a `skipping` message if something's
missing (a source file that doesn't exist yet, a theme with no `[palette]`
trying to use Qt). Check kitty, waybar, a GTK app, and a Qt app (Dolphin/
Kate/`qt6ct`-based settings if installed) actually changed.

## Step 14: commit

```
themes/catppuccin-latte/theme.toml
themes/catppuccin-latte/kitty/theme.conf
themes/catppuccin-latte/waybar/theme.css
themes/catppuccin-latte/rofi/theme.rasi
themes/catppuccin-latte/swaync/theme.css
themes/catppuccin-latte/lsd/theme.yaml
themes/catppuccin-latte/icons/mauve__Papirus-Light.tar   (if you baked a new accent)
themes/catppuccin-latte/gtk/theme.zip                    (if you bundled the GTK zip, Step 1)
themes/catppuccin-latte/qt/dotmanager-catppuccin-latte/
themes/catppuccin-latte/qt/dotmanager-catppuccin-latte.colors
dotfiles/nvim/.config/nvim/lua/config/theme.lua      (edited, not new)
core/theme_appliers/herdr_theme.py                   (edited, not new)
scripts/bake_icon_accents.py                          (if you added a COMBOS entry)
```

## Removing a theme

Delete `themes/<name>/` -- that one folder holds everything the theme owns.
Leftover `PROFILES` entries in `herdr_theme.py`/`theme.lua` are harmless to
leave behind (they only get read if some theme file still names them) but
fine to delete too.

## Adding support for a new app

Not covered by the eleven above -- say, fish's colorscheme. Write a module
in `core/theme_appliers/` with a function `apply(profile: dict) -> bool`
that reads `profile.get("your_key")` (and `profile.get("theme_dir")` if it
needs a per-theme file/folder) and does whatever that app needs; look at
`kitty_theme.py` for the simplest possible shape (file copy + reload) or
`herdr_theme.py` for one that edits part of a larger config with no
per-theme file at all. Add it to `PRE_LIVE_APPLIERS` or
`POST_LIVE_APPLIERS` in `core/theme_appliers/__init__.py` (see that file's
own docstring for which list, and why waybar/gtk ordering matters). That's
the whole extension point -- no registry, no entry points, no config schema
to satisfy.
