# dotmanager `backup` command reference

Encrypted backup & sync via restic (encryption, dedup, snapshots) + rclone
(transport to Dropbox). Passwords are never handled by dotmanager — restic
prompts for it interactively, or reads `RESTIC_PASSWORD` if you've exported
it for the session.

---

## `backup add`
Registers a folder as a backup target under a short name.

```
python3 main.py backup add zen-profile ~/.zen
python3 main.py backup add screenshots ~/Pictures/Screenshots
python3 main.py backup add coding-projects ~/dev
python3 main.py backup add "my notes" ~/Documents/notes
```

## `backup remove`
Drops a target from the list (does not touch any existing backed-up data).

```
python3 main.py backup remove screenshots
python3 main.py backup remove does-not-exist
```

## `backup list`
Prints every currently configured target and its path.

```
python3 main.py backup list
```

## `backup check`
Verifies restic and rclone are installed and the `dropbox` remote is configured, before you try `init`/`run`.

```
python3 main.py backup check
```

## `backup init`
Initializes the restic repository on Dropbox; safe to re-run, does nothing if already initialized.

```
python3 main.py backup init
```

## `backup run`
Backs up the given target(s) — or all of them — each as its own tagged snapshot.

```
python3 main.py backup run
python3 main.py backup run zen-profile
python3 main.py backup run zen-profile screenshots
python3 main.py backup run bogus-name
```

## `backup du`
Shows a size breakdown per target (plain `du`, no restic/rclone) so you can spot what's worth excluding before backing it up.

```
python3 main.py backup du
python3 main.py backup du zen-profile
python3 main.py backup du zen-profile screenshots
python3 main.py backup du zen-profile --depth 3
python3 main.py backup du --depth 2
```

## `backup snapshots`
Lists every snapshot currently stored in the repo.

```
python3 main.py backup snapshots
```

## `backup stats`
Shows the real total space the repo is using on Dropbox, after dedup and compression.

```
python3 main.py backup stats
```

## `backup restore`
Restores a snapshot into a target directory (defaults to a safe staging folder, not in place).

```
python3 main.py backup restore 9be6be21
python3 main.py backup restore latest
python3 main.py backup restore 9be6be21 --target ~/some/dir
python3 main.py backup restore latest --target /
```

## `backup forget`
Drops older snapshots and reclaims their space, keeping the N most recent per target.

```
python3 main.py backup forget
python3 main.py backup forget --keep-last 1
python3 main.py backup forget --keep-last 3
python3 main.py backup forget --keep-last 10
```

---

## Example day-to-day sequence

```
python3 main.py backup add project-x ~/dev/project-x
python3 main.py backup du project-x --depth 2
python3 main.py backup run project-x
python3 main.py backup stats
python3 main.py backup forget --keep-last 3
```
