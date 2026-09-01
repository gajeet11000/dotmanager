"""Applies a theme profile's GTK widget theme + light/dark color-scheme."""

from core.theme_appliers import _nwg_look


def apply(profile: dict) -> bool:
    fields = {}
    if "gtk_theme" in profile:
        fields["gtk-theme"] = profile["gtk_theme"]
    if "color_scheme" in profile:
        fields["color-scheme"] = profile["color_scheme"]

    if not fields:
        return False

    print(f"[gtk] gtk-theme={fields.get('gtk-theme', '(unchanged)')} "
          f"color-scheme={fields.get('color-scheme', '(unchanged)')}")
    _nwg_look.patch_fields(**fields)
    return True
