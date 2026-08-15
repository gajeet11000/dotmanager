from core import store

_SUFFIX_TO_KEY = {
    "aur": "aur",
    "flatpak": "flatpak",
}


def _parse_spec(spec: str) -> tuple[str, str]:
    """'name' -> ('official', name); 'name/aur' -> ('aur', name); 'name/flatpak' -> ('flatpak', name)."""
    if "/" in spec:
        name, suffix = spec.rsplit("/", 1)
        suffix = suffix.lower()
        if suffix not in _SUFFIX_TO_KEY:
            raise ValueError(
                f"Unknown suffix '/{suffix}' in '{spec}' (expected /aur or /flatpak)"
            )
        return _SUFFIX_TO_KEY[suffix], name
    return "official", spec


def add_packages(specs: list[str]) -> None:
    data = store.load()
    for spec in specs:
        list_key, name = _parse_spec(spec)
        if name in data[list_key]:
            print(f"'{name}' already in {list_key}, skipping")
            continue
        data[list_key].append(name)
        print(f"Added '{name}' to {list_key}")
    store.save(data)


def remove_packages(names: list[str]) -> None:
    data = store.load()
    for name in names:
        found_in = [key for key in store.LIST_KEYS if name in data[key]]
        if not found_in:
            print(f"'{name}' not found in any list")
            continue
        for key in found_in:
            data[key].remove(name)
        print(f"Removed '{name}' from {', '.join(found_in)}")
    store.save(data)
