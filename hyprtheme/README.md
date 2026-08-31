# hyprtheme

A tool that switches the colors of your apps all at once — terminal, status
bar, app launcher, GTK apps, whatever you use — by running one command. No
logging out, no restarting your whole desktop.

You've probably seen this before: pick "dark" or a named theme like
"Catppuccin", and everything on your screen changes together. That's what
this does, except _you_ tell it which theme goes with which app, since
everyone's setup is different.

It's not tied to any specific themes. It ships none. You bring your own
color files (or write plain hex colors directly), and this tool's job is
just to copy the right file to the right place and tell each app to reload.

## Before you start

You need:

- Python 3.11 or newer (`python3 --version` to check)
- Some apps that already support "themes" as separate files — most
  terminals and status bars do. If an app's config can `include` another
  file, or you can just overwrite one file to change its colors, it works
  with this.

You do **not** need to know Python to use this — you'll be writing two
small text files, not code.

If you only use the `pointer`/`copy`/`write` kinds described below (which
covers most apps), that's everything you need — no other packages. The
three **built-in plugins** each need one more thing installed, but only if
you actually use that plugin:

| Plugin | What it's for                          | Needs installed                                                                |
| ------ | --------------------------------------- | -------------------------------------------------------------------------------- |
| `gtk`  | GTK app theme + light/dark scheme       | [`nwg-look`](https://github.com/nwg-piotr/nwg-look) (any AUR/repo package by that name) |
| `icon` | Icon theme + accent color               | `nwg-look` (same as above); accent-color switching also wants [`papirus-folders`](https://github.com/PapirusDevelopmentTeam/papirus-folders) to bake the snapshots ahead of time (see the plugin's docstring) |
| `qt`   | Qt5/Qt6/KDE app colors                  | Kvantum (`kvantum` / `kvantum-qt5` package) for widget painting; optionally a platform engine that reads KDE `.colors` files for icon recoloring — on Hyprland that's [`hyprqt6engine`](https://github.com/hyprwm/hyprqt6engine) |

None of this is required to use hyprtheme itself — it's what the specific
built-in plugin shells out to or writes config for. If you're not theming
GTK/Qt apps, skip the table entirely.

The `qt` plugin also needs pre-built theme assets on disk (see "Adding a
new theme" below) — those are built by a separate package,
[hyprtheme-build](../hyprtheme-build/), which only *theme authors* need to
install, not everyday users of an already-set-up theme.

## Install it

```sh
pip install -e ./hyprtheme
```

This gives you a `hyprtheme` command.

## The 5-minute example

Say you use **kitty** (terminal) and want to switch its colors between two
themes you already have as files:

```
~/.config/kitty/themes/dracula.conf
~/.config/kitty/themes/nord.conf
```

And kitty's own `kitty.conf` has this line, which makes it read whatever
`current-theme.conf` says:

```
include current-theme.conf
```

(If your app doesn't have an "include" line like this yet, add one — check
its docs for how it lets you split config into multiple files.)

### 1. Tell hyprtheme where kitty's files live

Create `apps.toml`:

```toml
[apps.kitty]
kind = "pointer"
theme_key = "kitty_theme"
target = "~/.config/kitty/current-theme.conf"
source = "themes/{value}.conf"
pointer_format = "include themes/{value}.conf\n"
reload = ["pkill", "-USR1", "-x", "kitty"]
```

What this says: "kitty's active theme is controlled by the file at
`target`. When told to use theme `X`, write a line pointing at
`themes/X.conf`, then send kitty a signal to reload." (kitty specifically
reloads on `SIGUSR1` — check your own app's docs for how _it_ reloads, or
skip `reload` if it just rereads its config every time it runs, like most
launchers do.)

### 2. Create a theme

Create `themes/dracula.toml`:

```toml
name = "dracula"

[apps]
kitty_theme = "dracula"
```

`kitty_theme` here matches the `theme_key` from step 1 — this is what
connects the theme to the app. The value `"dracula"` is what gets
substituted into `{value}` above, so it resolves to
`~/.config/kitty/themes/dracula.conf` — the file you already have.

Do the same for `themes/nord.toml` with `kitty_theme = "nord"`.

### 3. Run it

```sh
hyprtheme --apps apps.toml --themes-dir themes/ list
# dracula
# nord

hyprtheme --apps apps.toml --themes-dir themes/ set dracula
```

kitty should recolor immediately. That's the whole loop: `apps.toml` says
_where_ things go, a theme file says _what_ value to put there.

## Adding a second app

Say you also use **waybar**, and its `style.css` does `@import
'current.css';`. Same idea — add another `[apps.*]` block:

```toml
[apps.waybar]
kind = "copy"
theme_key = "waybar_theme"
target = "~/.config/waybar/current.css"
source = "colors/{value}.css"
reload = ["killall", "-SIGUSR2", "waybar"]
```

Then add a matching line to each theme file:

```toml
[apps]
kitty_theme = "dracula"
waybar_theme = "dracula"
```

Any app you don't list in a theme's `[apps]` table is just skipped for
that theme — nothing breaks.

## The two `kind`s you'll use 90% of the time

- **`pointer`** — writes a one-line "include this file" statement. Use
  this when your app supports splitting its config into multiple files
  (kitty's `include`, swaync's `@import`, etc.).
- **`copy`** — replaces the target file's _entire contents_ with the
  source file's contents. Use this when the app just reads one file
  directly and has no include mechanism (most CSS-based bars, launchers).

(There's a third, `write`, for the rare app that has no per-theme file at
all — just a name it wants recorded somewhere. You likely won't need it
at first.)

## Common fields, quick reference

| Field             | Meaning                                                                                                   |
| ----------------- | --------------------------------------------------------------------------------------------------------- |
| `theme_key`       | The name this app looks for in a theme file's `[apps]` table                                              |
| `target`          | The file your app actually reads                                                                          |
| `source`          | Where to find the theme's file, relative to `target`'s folder                                             |
| `reload`          | Command to run after writing, so the app picks it up live (optional)                                      |
| `ok_reload_codes` | Exit codes from `reload` that just mean "app wasn't running" — not an error (optional, defaults to `[0]`) |

## When an app needs more than a file copy

Some apps don't have a themeable file at all — they need actual logic to
generate their colors (e.g. GTK apps, which read a system-wide settings
database rather than a plain file). For those, hyprtheme has a plugin
system instead of `apps.toml` fields — three are built in (`gtk`, `icon`,
`qt`) for exactly this. You won't need to write your own unless you're
theming something unusual; see [PLUGINS.md](PLUGINS.md) when you get
there.

The `qt` plugin is a special case worth calling out: Qt/KDE apps need a
whole generated Kvantum theme + color-scheme file, not just a value copied
into place. That generation lives in a **separate package**,
[hyprtheme-build](../hyprtheme-build/) — see below. `hyprtheme` itself
never depends on it; installing just the switcher pulls in none of this.

## Adding a new theme

Nothing here requires writing Python. If you're not using the `qt` plugin,
it's just steps 1–2:

1. Pick colors for the apps you've configured (a `[palette]` table of hex
   values, if any plugin you use needs one — `qt` does).
2. Write `themes/<name>.toml` — copy an existing theme file as a starting
   point, one line per app's `theme_key`.
3. **Only if you use the `qt` plugin**: it reads a pre-built Kvantum theme
   and `.colors` file rather than generating them live, since a theme's
   palette is a fixed preset, not something computed at switch time — no
   reason to redo that work on every `set`. Install the separate builder
   once (`pip install -e ./hyprtheme-build`), then build the new theme's
   assets:
   ```sh
   hyprtheme-build qt themes/<name>.toml \
     --base-svg-dark   assets/kvantum/base-dark.svg \
     --base-svg-light  assets/kvantum/base-light.svg \
     --kvconfig-template assets/kvantum/base.kvconfig.template \
     --kvantum-out     assets/generated/kvantum \
     --colors-out      assets/generated/color-schemes
   ```
   Commit the theme file together with what this writes under
   `assets/generated/`. From then on, `theme set <name>` just copies that
   output into place — it never touches the builder again for this theme.
4. `hyprtheme --apps apps.toml --themes-dir themes/ set <name>` to verify.

Removing a theme is the mirror image: delete `themes/<name>.toml` (and its
`assets/generated/` output, if you built one).

## Python, if you want it

```python
from pathlib import Path
from hyprtheme import ThemeManager

manager = ThemeManager(apps_path=Path("apps.toml"), themes_dir=Path("themes"))
manager.list_themes()
manager.set_theme("dracula")
```
