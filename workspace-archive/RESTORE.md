# Karere laptop migration snapshot — 9 October 2026

The current source is published on
[`feat/vulkan-adaptive-refresh`](https://github.com/sknowledge1/karere/tree/feat/vulkan-adaptive-refresh)
at `aa39432cdeec0c15ad87ad7b21de4437e12204e9`.
This separate backup branch adds the laptop's workspace reports, diagnostic
captures, compiled measurement binaries and validation evidence. The
`source-history.bundle` preserves the complete Git history and references as
they stood before the archive commit. `manifest.json` lists the published source
branches and the exact size, SHA-256 and executable permissions of each archived
file. The archives retain the original workspace-relative paths.

## Continue development on the new computer

```sh
git clone https://github.com/sknowledge1/karere.git karere
cd karere
git switch feat/vulkan-adaptive-refresh
git remote add upstream https://github.com/tobagin/karere.git
```

The fork is named `origin` in this fresh clone. The old laptop used `fork` for
the personal repository and `origin` for the maintainer's repository.
The graphics PR remains draft: the conditional native-handle CEF engine still
needs rebuilding and hardware validation. Read
[`COMPATIBILITY_VALIDATION.md`](../tools/scrolling-probe/COMPATIBILITY_VALIDATION.md)
for the checks already completed and remaining delivery gates.

## Retrieve and verify the saved evidence

From the fresh clone:

```sh
git worktree add ../karere-migration origin/backup/laptop-migration-2026-10-09
python3 ../karere-migration/workspace-archive/verify_backup.py
git bundle verify ../karere-migration/workspace-archive/source-history.bundle
```

The verifier hashes every report, archive and bundle, then decompresses and
hashes every archive member. Successful verification confirms that the raw
captures and binaries match the manifest without extracting them.
Reports are also readable directly in `workspace-archive/reports/`; their
original relative links refer to the old worktree layout restored below.

## Restore the original workspace layout (optional)

Start in a new, empty directory called `karere-workspace`. Replace `archive_dir`
with the absolute path to the downloaded `workspace-archive` directory:

```sh
archive_dir=/absolute/path/to/karere-migration/workspace-archive
git clone https://github.com/sknowledge1/karere.git upstream
git -C upstream remote rename origin fork
git -C upstream remote add origin https://github.com/tobagin/karere.git
git -C upstream fetch origin
git -C upstream switch diagnostics/cef-scroll-stalls-173
git -C upstream worktree add ../conversation-upstream diagnostics/conversation-scroll-432
git -C upstream worktree add ../wallpaper-upstream fix/conversation-wallpaper-raster
git -C upstream worktree add ../acceleration-upstream feat/vulkan-adaptive-refresh
cp -p "$archive_dir"/reports/* .
for saved_archive in "$archive_dir"/evidence/*.tar.gz; do
    tar -xzf "$saved_archive" -C .
done
```

If network access is unavailable, clone `source-history.bundle` instead and
fetch the listed source branches from it. The bundle contains the source before
the archive commit; keep the downloaded archive directory beside that clone.

Cargo dependency caches, build intermediates, Python/Ruff caches and temporary
test profiles are regenerable and are excluded. The standalone measurement
binaries and probes used for the recorded results are preserved. Credentials
and actual application account profiles are not part of this source backup.
The saved captures contain numeric rendering measurements; trace arguments
were stripped by the collectors. The installed Flatpak and its dependencies
can be installed again on the new computer.
