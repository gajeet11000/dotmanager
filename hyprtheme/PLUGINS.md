# Plugins: theming GTK, icons, and Qt/KDE apps

The main [README](README.md) covers apps that just need a file copied in
(`pointer`/`copy`/`write`). Some apps can't work that way — GTK apps read a
system-wide settings database rather than a plain file, and Qt/KDE apps
need a whole generated theme, not a value substitution. For those,
hyprtheme has three **built-in plugins**: `gtk`, `icon`, `qt`.

This doc continues the README's running example — **Catppuccin Latte** —
and extends it to cover all three. Same two-phase shape every time:

1. **Install/build the theme's materials first.** Nothing here touches
   hyprtheme yet — you're just getting the actual GTK theme, icon theme,
   and (for Qt) generated Kvantum files onto disk.
2. **Then wire it into `apps.toml` and your theme file**, same pattern as
   the file-swap apps.

## What each plugin needs installed

| Plugin | What it's for                     | Needs installed                                                                          |
| ------ | ---------------------------------- | ----------------------------------------------------------------------------------------- |
| `gtk`  | GTK app theme + light/dark scheme  | [`nwg-look`](https://github.com/nwg-piotr/nwg-look) (any AUR/repo package by that name)   |
| `icon` | Icon theme + accent color          | `nwg-look` (same as above); accent-color switching also wants [`papirus-folders`](https://github.com/PapirusDevelopmentTeam/papirus-folders) |
| `qt`   | Qt5/Qt6/KDE app colors             | Kvantum (`kvantum`/`kvantum-qt5` package); optionally a platform engine reading KDE `.colors` files — on Hyprland, [`hyprqt6engine`](https://github.com/hyprwm/hyprqt6engine) |

None of this is needed if you're not using that specific plugin.

`gtk` and `icon` share one more one-time prerequisite: **run `nwg-look`
once** (open the GUI and close it again, or `nwg-look -x` on the command
line) before your first `theme set`. That's what creates
`~/.local/share/nwg-look/gsettings`, the file these two plugins patch —
they edit existing lines in it, they don't create the file from nothing.

## Phase 1: installing Catppuccin Latte's GTK, icon, and Qt materials

### GTK theme

Install a Catppuccin Latte GTK theme (AUR has one, or grab a release from
[catppuccin/gtk](https://github.com/catppuccin/gtk)) so it lands under
`/usr/share/themes/` or `~/.local/share/themes/`. Note its exact folder
name — you'll need it verbatim in the theme file. For example:

```
~/.local/share/themes/catppuccin-latte-mauve-standard+default/
```

### Icon theme

Pick an icon theme that ships a light variant — Papirus is common and has
one (`Papirus-Light`), usually available as the `papirus-icon-theme`
package. If you also want an accent color on top (folder icons tinted to
match the theme), bake it once with `papirus-folders -C <accent> --theme
Papirus-Light` — see the built-in `icon` plugin's docstring
(`src/hyprtheme/appliers/icon.py`) for the snapshot-based setup that avoids
re-running this live on every switch.

### Qt/Kvantum theme

This is generated, not installed as a package — from a separate tool,
[hyprtheme-build](../hyprtheme-build/), so that switching a theme never
needs to depend on it.

```sh
pip install -e ./hyprtheme-build
```

You need three template inputs once, reusable across every theme you ever
add:

- A **dark base SVG** and a **light base SVG** — copy the `.svg` from any
  installed Kvantum theme matching each polarity, with all hardcoded
  `fill="#..."` colors stripped out (a pure shape template).
- A **`.kvconfig` template** — copy a real theme's `.kvconfig`, with every
  hex color replaced by an `@ROLE@` token (`@WINDOW@`, `@ACCENT@`, `@TEXT@`,
  ...) — see `build_tokens()` in
  `hyprtheme-build/src/hyprtheme_build/kvantum.py` for the exact token set.

Then, once your theme file has a `[palette]` table (next section), build
its Qt assets:

```sh
hyprtheme-build qt themes/catppuccin-latte.toml \
  --base-svg-dark    assets/kvantum/base-dark.svg \
  --base-svg-light   assets/kvantum/base-light.svg \
  --kvconfig-template assets/kvantum/base.kvconfig.template \
  --kvantum-out      assets/generated/kvantum \
  --colors-out       assets/generated/color-schemes
```

This writes `assets/generated/kvantum/hyprtheme-catppuccin-latte/` (the
Kvantum theme) and `assets/generated/color-schemes/hyprtheme-catppuccin-latte.colors`.
Commit both — this is a one-time build, not something `theme set` redoes
on every switch. See [hyprtheme-build's README](../hyprtheme-build/README.md)
for more on why it's a separate package.

## Phase 2: wiring it all into hyprtheme

### Extend the theme file

Add to `themes/catppuccin-latte.toml` (alongside `kitty_theme`/
`waybar_theme` from the main README):

```toml
name = "catppuccin-latte"

[apps]
kitty_theme = "catppuccin-latte"
waybar_theme = "catppuccin-latte"
gtk_theme = "catppuccin-latte-mauve-standard+default"
color_scheme = "prefer-light"
icon_theme = "Papirus-Light"
icon_accent = "mauve"

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

`[palette]` is only read by plugins that generate colors rather than
pointing at a pre-made file — `qt` is the only built-in one that needs it.
The hex values above are Catppuccin's own published Latte palette.

### Extend `apps.toml`

```toml
[apps.gtk]
kind = "plugin"
plugin = "gtk"
live_push = "nwg-look"
gsettings_file = "~/.local/share/nwg-look/gsettings"
theme_dirs = ["/usr/share/themes", "~/.local/share/themes"]

[apps.icon]
kind = "plugin"
plugin = "icon"
live_push = "nwg-look"
gsettings_file = "~/.local/share/nwg-look/gsettings"
assets_dir = "~/dotfiles-assets/icon-themes"

[apps.qt]
kind = "plugin"
plugin = "qt"
kvantum_dir = "~/.config/Kvantum"
generated_kvantum_dir = "assets/generated/kvantum"
generated_colors_dir = "assets/generated/color-schemes"
kdeglobals = "~/.config/kdeglobals"
# only if you're using a platform engine, e.g. hyprqt6engine on Hyprland:
platform_engine_conf = "~/.config/hypr/hyprqt6engine.conf"
```

`gtk` and `icon` both set `live_push = "nwg-look"` — they patch the same
file, and nwg-look's own re-export step re-reads *everything*, not just
what changed, so batching means it only runs once per switch instead of
twice. See "Batching a shared reload step" below for the mechanics.

### Verify

```sh
hyprtheme --apps apps.toml --themes-dir themes/ set catppuccin-latte
```

Check a GTK app, an icon (e.g. a file manager), and a Qt app (e.g.
`qt6ct`-based settings, or Dolphin/Kate if installed) actually changed.

## Adding a later theme's Qt assets

Once this is wired up, adding e.g. `catppuccin-mocha` (dark) later is just
Phase 1's Qt step repeated — `hyprtheme-build qt themes/catppuccin-mocha.toml
...` with the same template inputs — plus a new theme file. `apps.toml`
doesn't change.

---

## Writing your own plugin

Reach for a plugin only when an app needs real logic: generating colors
from a raw palette instead of pointing at a pre-made file, editing one
section of a larger config instead of the whole file, or sharing a reload
step across multiple apps.

A plugin is a Python module with a module-level function:

```python
def apply(theme: hyprtheme.Theme, app: hyprtheme.AppConfig) -> bool:
    ...  # return True if it did anything, False to no-op (e.g. the theme
         # has no relevant key) -- set_theme() doesn't care either way
```

`theme.apps` is the theme's `[apps]` table (plain strings); `theme.palette`
is its optional `[palette]` table of raw hex colors, if the theme provides
one. `app.options` is every key in the app's `apps.toml` stanza that isn't
one of the built-in fields (`kind`, `target`, `reload`, ...) — your
plugin's own config, same as `gsettings_file`/`theme_dirs`/etc. above.

Reference it from `apps.toml`:

```toml
[apps.my_app]
kind = "plugin"
plugin = "my_app"      # a name resolved via one of the two methods below
```

### Registering it

Two ways, same as the three built-ins use:

- **Entry point** — add `hyprtheme.appliers` to your own package's
  `pyproject.toml` (see hyprtheme's own for the pattern) and `pip install`
  it. Every consumer that has your package installed gets it
  automatically, no per-machine wiring.
- **Local plugin directory** — no packaging at all. Point
  `ThemeManager(plugin_dirs=[Path("my_plugins")])` (or the CLI's
  `--plugin-dir`) at a directory; every `*.py` file in it is imported and
  its `apply` registered under the file's stem. This is how you'd keep a
  personal/niche app (something only you use) out of a shared library.

### Batching a shared reload step (`live_push`)

Some apps share one expensive "push it live" step that only needs to run
once no matter how many of them changed — the `gtk`/`icon` pair above is
the example: both patch fields into the same nwg-look-managed file, and
nwg-look's own re-export step re-reads *everything*, not just what
changed. Give apps that need this the same `live_push` value; `ThemeManager`
runs every app sharing that value together, then calls a plugin registered
as `f"{live_push}:post"` once (the built-in pair uses `"nwg-look:post"`) —
no arguments, called for its side effect only.

## Built-in plugins reference

See the docstring at the top of each for exactly what `options` keys it
expects: `src/hyprtheme/appliers/gtk.py`, `icon.py`, `qt.py`.
