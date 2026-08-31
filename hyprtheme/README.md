# hyprtheme

A theme switcher for Hyprland (or any Linux desktop) — swap colors across
your terminal, bar, launcher, GTK, Qt/KDE apps and anything else with a
config file, live, no logout needed. Framework, not a fixed theme set: it
ships zero themes and knows nothing about your dotfiles layout until you
tell it, via two kinds of file you write yourself.

```sh
pip install -e ./hyprtheme     # or from a real install: pip install hyprtheme
hyprtheme --apps apps.toml --themes-dir themes/ list
hyprtheme --apps apps.toml --themes-dir themes/ set catppuccin-mocha
```

## The two files you write

**`apps.toml`** — one `[apps.<name>]` table per application, describing
*where* its config lives and *how* to apply a value to it. This is
per-installation config: write it once for your own dotfiles layout.

**`themes/<name>.toml`** — one file per theme, describing *what* value each
app should get. Add a theme by dropping a file here; remove one by deleting
it. No code involved either way.

```toml
# themes/catppuccin-mocha.toml
name = "catppuccin-mocha"

[apps]
kitty_theme = "catppuccin-mocha"     # matches an [apps.kitty] app below
waybar_theme = "catppuccin-mocha"
gtk_theme = "catppuccin-mocha-mauve"

[palette]                             # only needed by plugins that
base = "dark"                         # generate colors instead of pointing
bg = "#1e1e2e"                        # at a pre-made theme file (see the
fg = "#cdd6f4"                        # built-in `qt` plugin)
accent = "#cba6f7"
# ...
```

## Adding an app

Most apps need nothing but a `[apps.<name>]` table — no Python. Two kinds:

```toml
# "pointer": writes a one-line include statement, for formats with an
# include mechanism (kitty's `include`, swaync's `@import`).
[apps.kitty]
kind = "pointer"
theme_key = "kitty_theme"                       # key read from the theme's [apps]
target = "~/.config/kitty/current-theme.conf"   # file kitty actually reads
source = "themes/{value}.conf"                  # resolved relative to target's dir
pointer_format = "include themes/{value}.conf\n"
reload = ["pkill", "-USR1", "-x", "kitty"]       # optional
ok_reload_codes = [0, 1]                         # 1 = nothing running, fine

# "copy": overwrites target with source's full contents, for formats with
# no include mechanism (waybar, rofi, most CSS/YAML-style configs).
[apps.waybar]
kind = "copy"
theme_key = "waybar_theme"
target = "~/.config/waybar/colors/current.css"
source = "colors/{value}.css"
reload = ["your-restart-script"]
```

If an app needs real logic — generating colors from `[palette]` instead of
pointing at a pre-made file, editing one section of a larger config,
batching a shared live-reload step across multiple apps (see `live_push`
below) — write a **plugin** instead: a Python module with a module-level

```python
def apply(theme: hyprtheme.Theme, app: hyprtheme.AppConfig) -> bool:
    ...  # return True if it did anything, False to no-op (e.g. theme has
         # no relevant key) — set_theme() doesn't care either way
```

and reference it from `apps.toml`:

```toml
[apps.qt]
kind = "plugin"
plugin = "qt"          # a name resolved via the plugin registry (below)
# ...anything else here lands in app.options, for the plugin to read
```

Three plugins ship built in — `gtk`, `icon`, `qt` — see their own module
docstrings under `src/hyprtheme/appliers/` for exactly what `options` keys
each expects.

### Registering a plugin

Two ways, same as the three built-ins use:

- **Entry point** — add `hyprtheme.appliers` to your own package's
  `pyproject.toml` (see this package's own for the pattern) and
  `pip install` it; every consumer that has your package installed gets it
  automatically, no per-machine wiring.
- **Local plugin directory** — no packaging at all. Point
  `ThemeManager(plugin_dirs=[Path("my_plugins")])` (or the CLI's
  `--plugin-dir`) at a directory; every `*.py` file in it is imported and
  its `apply` registered under the file's stem. This is how you'd keep a
  personal/niche app (something only you use) out of a shared library.

### `live_push`: batching a shared reload step

Some apps share one expensive "push it live" step that only needs to run
once no matter how many of them changed — e.g. `gtk` and `icon` both patch
fields into the same nwg-look-managed file, and nwg-look's own re-export
step re-reads *everything*, not just what changed. Give apps that need this
the same `live_push` value:

```toml
[apps.gtk]
kind = "plugin"
plugin = "gtk"
live_push = "nwg-look"
# ...

[apps.icon]
kind = "plugin"
plugin = "icon"
live_push = "nwg-look"
# ...
```

`ThemeManager` runs every app sharing a `live_push` group together, then
calls a plugin registered as `f"{live_push}:post"` once (the built-in
`gtk`/`icon` pair uses `"nwg-look:post"`, wired to the same nwg-look
`apply_live()` call both need) — no args, called for its side effect only.

## Python API

```python
from pathlib import Path
from hyprtheme import ThemeManager

manager = ThemeManager(
    apps_path=Path("apps.toml"),
    themes_dir=Path("themes"),
    plugin_dirs=[Path("my_plugins")],   # optional
)
manager.list_themes()      # -> ["catppuccin-mocha", ...]
manager.set_theme("catppuccin-mocha")
```
