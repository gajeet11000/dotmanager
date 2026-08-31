# hyprtheme

A tool that switches the colors of your apps all at once — terminal, status
bar, app launcher, GTK apps, whatever you use — by running one command. No
logging out, no restarting your whole desktop.

You've probably seen this before: pick "dark" or a named theme like
"Catppuccin", and everything on your screen changes together. That's what
this does, except _you_ tell it which theme goes with which app, since
everyone's setup is different.

It's not tied to any specific themes. It ships none. You bring your own
color files (or plain hex colors), and this tool's job is just to copy the
right file to the right place and tell each app to reload.

This README walks through one concrete example start to finish — installing
**Catppuccin Latte** (a light theme) for kitty and waybar — then shows how
to extend the same theme to GTK/icon/Qt apps too. By the end you'll have a
working `hyprtheme set catppuccin-latte` and enough to repeat the pattern
for any other theme.

## Before you start

You need:

- Python 3.11 or newer (`python3 --version` to check)
- Some apps that already support "themes" as separate files — most
  terminals and status bars do. If an app's config can `include` another
  file, or you can just overwrite one file to change its colors, it works
  with this.

You do **not** need to know Python to use this — you'll be writing two
small text files, not code.

## Install it

```sh
pip install -e ./hyprtheme
```

This gives you a `hyprtheme` command.

## The example: Catppuccin Latte for kitty and waybar

Two apps, both already themeable by dropping in a file — no plugins needed
yet.

### 1. Get the theme's color files

Catppuccin ships ready-made config files for both apps:

- kitty: [catppuccin/kitty's `latte.conf`](https://github.com/catppuccin/kitty)
  → save it as `~/.config/kitty/themes/catppuccin-latte.conf`
- waybar: [catppuccin/waybar's `latte.css`](https://github.com/catppuccin/waybar)
  → save it as `~/.config/waybar/colors/catppuccin-latte.css`

(This step is the same no matter what tool you use to switch themes —
you're just getting the raw color files onto disk. hyprtheme doesn't care
where they came from.)

### 2. Make sure each app can be pointed at a file

kitty's `kitty.conf` needs an `include` line so it'll read whatever
`current-theme.conf` says:

```
include current-theme.conf
```

waybar's `style.css` needs the equivalent:

```css
@import "colors/current.css";
```

(If your app doesn't have this yet, check its docs for how it lets you
split config into multiple files — most terminals and bars support this.)

### 3. Tell hyprtheme where each app's files live

Create `apps.toml`:

```toml
[apps.kitty]
kind = "pointer"
theme_key = "kitty_theme"
target = "~/.config/kitty/current-theme.conf"
source = "themes/{value}.conf"
pointer_format = "include themes/{value}.conf\n"
reload = ["pkill", "-USR1", "-x", "kitty"]

[apps.waybar]
kind = "copy"
theme_key = "waybar_theme"
target = "~/.config/waybar/colors/current.css"
source = "{value}.css"
reload = ["/bin/sh", "-c", "pkill -x waybar; sleep 0.3; setsid waybar >/dev/null 2>&1 </dev/null &"]
```

What each line means: `target` is the file the app actually reads.
`source` says where to find the theme's own file (relative to `target`'s
folder), with `{value}` filled in from the theme. `kitty` uses `pointer`
(write a one-line `include`) since kitty supports that; `waybar` uses
`copy` (overwrite the whole file) since its CSS doesn't split as cleanly.
`reload` is the command that makes the running app pick up the change —
optional, skip it if your app just rereads its config every launch.

### 4. Create the theme

Create `themes/catppuccin-latte.toml`:

```toml
name = "catppuccin-latte"

[apps]
kitty_theme = "catppuccin-latte"
waybar_theme = "catppuccin-latte"
```

`kitty_theme` and `waybar_theme` match the `theme_key`s from step 3 — that's
what connects a theme to an app. The value `"catppuccin-latte"` is what
gets substituted into `{value}`, so it resolves to the files you saved in
step 1.

### 5. Run it

```sh
hyprtheme --apps apps.toml --themes-dir themes/ list
# catppuccin-latte

hyprtheme --apps apps.toml --themes-dir themes/ set catppuccin-latte
```

kitty and waybar should recolor immediately. That's the whole loop:
`apps.toml` says _where_ things go, a theme file says _what_ value to put
there.

## The two `kind`s you'll use 90% of the time

- **`pointer`** — writes a one-line "include this file" statement. Use
  this when your app supports splitting its config into multiple files.
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

## Going further: GTK, icons, and Qt apps for the same theme

kitty and waybar both just needed a file. Some apps don't have a themeable
file at all — GTK apps read a system-wide settings database, and Qt/KDE
apps need a whole generated theme, not a value to copy in. hyprtheme has
three **built-in plugins** for exactly these — `gtk`, `icon`, `qt` — so you
can extend the Catppuccin Latte example to cover them too.

The key difference from the file-swap apps above: **the plugin's raw
materials have to be installed/built _before_ you wire them into
`apps.toml`**, in two separate phases:

1. **Install/build the theme's materials** — get the actual GTK theme
   package on disk, pick an icon theme, and (for `qt`) generate its Kvantum
   files. This step doesn't involve hyprtheme at all yet.
2. **Integrate it with the switcher** — add the `[apps.*]` plugin stanzas
   and the matching keys in your theme file, then `hyprtheme set` to verify.

[PLUGINS.md](PLUGINS.md) walks through exactly this, continuing the same
Catppuccin Latte example — installing the GTK/icon theme, building the Qt
assets with the separate `hyprtheme-build` package, then wiring all three
into `apps.toml`. If you only need file-swap apps, you can stop reading
here.

## Adding another theme later

Once one theme works, adding a second is short: repeat steps 1 and 4 above
for the new theme's files (skip 2 and 3 — the app wiring in `apps.toml`
doesn't change), and drop a new `themes/<name>.toml`. Any app you don't
list in a theme's `[apps]` table is just skipped for that theme — nothing
breaks. Removing a theme is deleting its `.toml` file, nothing else.

## Python, if you want it

```python
from pathlib import Path
from hyprtheme import ThemeManager

manager = ThemeManager(apps_path=Path("apps.toml"), themes_dir=Path("themes"))
manager.list_themes()
manager.set_theme("catppuccin-latte")
```
