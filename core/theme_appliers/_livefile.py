from pathlib import Path


def write(path: Path, content: str) -> None:
    """Write `content` to `path`, replacing it with a plain file.

    Several "current theme" files (kitty's current-theme.conf, waybar's
    current.css, ...) used to live inside their app's dotfiles/ package and
    get stow-symlinked into place -- which meant every `theme set` wrote
    straight into a git-tracked file, dirtying the repo on every switch.
    They're no longer part of any dotfiles/ package, but a machine that
    still has the old stow-created symlink lying around would otherwise
    have this write land back inside the repo (following the symlink to
    its now-deleted target's parent dir). Removing any existing symlink
    first guarantees a real, untracked file ends up at `path`.
    """
    if path.is_symlink():
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
