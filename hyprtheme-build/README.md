# hyprtheme-build

The asset generator for [hyprtheme](../hyprtheme/) themes. It's a separate
package from `hyprtheme` on purpose: `hyprtheme` (the switcher) has zero
dependency on this, so switching a theme never pulls in or runs any of this
code. You only need `hyprtheme-build` if you're *adding a new theme* that
uses hyprtheme's built-in `qt` plugin — everyday theme switching doesn't
touch it.

This README builds the Qt/KDE assets for the same running example as
hyprtheme's own docs — **Catppuccin Latte** — picking up right where
[PLUGINS.md](../hyprtheme/PLUGINS.md)'s "Phase 1: installing Catppuccin
Latte's ... Qt materials" section leaves off. Read that first if you
haven't set up the theme file yet.

## Why this exists

Kvantum (Qt/KDE widget theming) needs a generated SVG + `.kvconfig`, and
KDE apps' icon recoloring needs a generated `.colors` file — both rendered
from a theme's raw `[palette]` table (hex colors). A theme's palette is a
fixed preset, not something computed live, so that rendering only needs to
happen once, ever, per theme — not on every `theme set`. This package does
that one-time render; hyprtheme's `qt` plugin just points at its output at
switch time (a symlink created once, never copied).

## Install

```sh
pip install -e ./hyprtheme-build
```

(Pulls in `hyprtheme` itself, since it reads theme `.toml` files the same
way the switcher does — you don't need to install `hyprtheme` separately
first.)

## Walkthrough: building Catppuccin Latte's Qt assets

You need two things prepared once, reusable for every theme you ever add
(not just this one):

1. **Two base SVGs**, one per light/dark polarity — `base-dark.svg` and
   `base-light.svg`. Copy the `.svg` from any installed Kvantum theme
   matching each polarity (any Kvantum theme folder under
   `~/.config/Kvantum/` or `/usr/share/Kvantum/` has one), then strip every
   hardcoded color out of it (`grep 'fill="#'` should match nothing when
   you're done) — you want a pure shape template, safe to recolor for any
   palette.
2. **A `.kvconfig` template** — copy a real theme's `.kvconfig` (same
   source theme works fine), and replace every hex color in it with an
   `@ROLE@` token: `@WINDOW@`, `@BASE@`, `@BUTTON@`, `@LIGHT@`,
   `@HIGHLIGHT_ALPHA@`, `@TEXT@`, `@MUTED@`, `@DIM_TEXT@`, `@ACCENT@`,
   `@LINK_VISITED@`, `@ON_ACCENT@`. See `build_tokens()` in
   `src/hyprtheme_build/kvantum.py` for exactly what each token gets filled
   with from a theme's `[palette]`. Leave structure/geometry/widget-state
   settings untouched — only the color values change.

Save both under, say, `assets/kvantum/` next to your theme files.

With `themes/catppuccin-latte.toml` already having a `[palette]` table
(see PLUGINS.md's Phase 2 for the exact values), build its assets:

```sh
hyprtheme-build qt themes/catppuccin-latte.toml \
  --base-svg-dark    assets/kvantum/base-dark.svg \
  --base-svg-light   assets/kvantum/base-light.svg \
  --kvconfig-template assets/kvantum/base.kvconfig.template \
  --kvantum-out      assets/generated/kvantum \
  --colors-out       assets/generated/color-schemes
```

Since Catppuccin Latte's `[palette]` has `base = "light"`, this uses your
`base-light.svg`. Output:

```
assets/generated/kvantum/hyprtheme-catppuccin-latte/
  hyprtheme-catppuccin-latte.kvconfig
  hyprtheme-catppuccin-latte.svg
assets/generated/color-schemes/
  hyprtheme-catppuccin-latte.colors
```

**Commit both** alongside `themes/catppuccin-latte.toml` — this is the
one-time build, not something regenerated later. hyprtheme's `qt` plugin
(configured with `generated_kvantum_dir`/`generated_colors_dir` pointing at
these two folders — see PLUGINS.md's `apps.toml` snippet) picks this exact
output up on `theme set`.

## Adding another theme later

Same command, new theme file — the two base SVGs and the kvconfig template
are reusable across every theme, you built those once. Only run this again
when a theme's `[palette]` changes or a new theme is added.
