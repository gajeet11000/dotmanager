"""Build-time asset generator for hyprtheme themes: turns a theme's raw
`[palette]` table into a Kvantum theme + KDE `.colors` file. A separate
package from `hyprtheme` itself -- switching a theme never imports this,
only building one does. Run by hand, once, when adding a new theme
(`hyprtheme-build qt ...`); see hyprtheme's README, "Adding a new theme".
"""
