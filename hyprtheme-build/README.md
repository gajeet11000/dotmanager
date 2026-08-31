# hyprtheme-build

Build-time asset generator for [hyprtheme](../hyprtheme/) themes. This is a
separate package from `hyprtheme` on purpose: `hyprtheme` (the switcher) has
zero dependency on this, so switching a theme never pulls in or runs any of
this code. You only need `hyprtheme-build` if you're *adding a new theme*
that uses hyprtheme's built-in `qt` plugin.

## Why this exists

Kvantum (Qt/KDE widget theming) needs a generated SVG + `.kvconfig`, and KDE
apps' icon recoloring needs a generated `.colors` file -- both rendered from
a theme's raw `[palette]` table (hex colors). Since a theme's palette is a
fixed preset, not something computed live, that rendering only needs to
happen once, ever, per theme -- not on every `theme set`. This package does
that one-time render; hyprtheme's `qt` plugin just copies its output into
place at switch time.

## Install

```sh
pip install -e ./hyprtheme-build
```

(Pulls in `hyprtheme` itself, since it reads theme `.toml` files the same
way the switcher does.)

## Use

```sh
hyprtheme-build qt themes/<name>.toml \
  --base-svg-dark    assets/kvantum/base-dark.svg \
  --base-svg-light   assets/kvantum/base-light.svg \
  --kvconfig-template assets/kvantum/base.kvconfig.template \
  --kvantum-out      assets/generated/kvantum \
  --colors-out       assets/generated/color-schemes
```

Writes `<kvantum-out>/hyprtheme-<name>/` (the Kvantum theme folder) and
`<colors-out>/hyprtheme-<name>.colors`. Commit both alongside the theme
file -- see hyprtheme's README, "Adding a new theme", for the full
checklist and what the two base SVGs / kvconfig template need to look like.
