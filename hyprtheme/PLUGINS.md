# Writing a plugin

Most apps just need an `apps.toml` stanza (see the main README) — no code.
Reach for a plugin only when an app needs real logic: generating colors
from a raw palette instead of pointing at a pre-made file, editing one
section of a larger config instead of the whole file, or sharing a
reload step across multiple apps.

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
plugin's own config.

Reference it from `apps.toml`:

```toml
[apps.qt]
kind = "plugin"
plugin = "qt"          # a name resolved via one of the two methods below
# ...anything else here lands in app.options
```

## Registering it

Two ways, same as the three built-ins (`gtk`, `icon`, `qt`) use:

- **Entry point** — add `hyprtheme.appliers` to your own package's
  `pyproject.toml` (see this package's own for the pattern) and
  `pip install` it. Every consumer that has your package installed gets it
  automatically, no per-machine wiring.
- **Local plugin directory** — no packaging at all. Point
  `ThemeManager(plugin_dirs=[Path("my_plugins")])` (or the CLI's
  `--plugin-dir`) at a directory; every `*.py` file in it is imported and
  its `apply` registered under the file's stem. This is how you'd keep a
  personal/niche app (something only you use) out of a shared library.

## Batching a shared reload step (`live_push`)

Some apps share one expensive "push it live" step that only needs to run
once no matter how many of them changed — e.g. the built-in `gtk` and
`icon` plugins both patch fields into the same nwg-look-managed file, and
nwg-look's own re-export step re-reads *everything*, not just what
changed. Give apps that need this the same `live_push` value:

```toml
[apps.gtk]
kind = "plugin"
plugin = "gtk"
live_push = "nwg-look"

[apps.icon]
kind = "plugin"
plugin = "icon"
live_push = "nwg-look"
```

`ThemeManager` runs every app sharing a `live_push` group together, then
calls a plugin registered as `f"{live_push}:post"` once (the built-in pair
above uses `"nwg-look:post"`) — no arguments, called for its side effect
only.

## Built-in plugins

See the docstring at the top of each for exactly what `options` keys it
expects: `src/hyprtheme/appliers/gtk.py`, `icon.py`, `qt.py`.
