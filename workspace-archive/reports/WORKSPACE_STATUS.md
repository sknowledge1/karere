# Karere workspace — 9 October 2026

The workspace root contains reports and linked Git worktrees. Run Git commands
inside a checkout, or use `git -C <checkout> ...`.

| Checkout | Branch | Role |
| --- | --- | --- |
| `upstream` | `diagnostics/cef-scroll-stalls-173` | Clean historical #191 branch; merged upstream |
| `conversation-upstream` | `diagnostics/conversation-scroll-432` | Original v4.3.2 diagnostics published at `2d7dd40`; raw captures preserved in the migration archive |
| `wallpaper-upstream` | `fix/conversation-wallpaper-raster` | Reviewed #193 tools and original wallpaper fix; fast-forwarded to the fork's existing upstream integration at `6b03fa1` |
| `acceleration-upstream` | `feat/vulkan-adaptive-refresh` | Current local development checkout; integrates upstream 4.3.4, reviewed #193 tools and GPU compatibility follow-up |

The development checkout is clean at published commit `aa39432`, including both
integrations and the compatibility follow-up. The other three worktrees are
clean. Local `main`, `origin/main` and `fork/main` match at `10bba03`.
Stable Karere is installed at
4.3.4, deployment `7928a66fca79343fa12a89fc9afacc607a69e8ff9f5173504066331337dca8eb`,
using GNOME Platform 51. These changes do not install a new application.

## Published work

- [#191](https://github.com/tobagin/karere/pull/191) is merged; its scheduler fix ships in stable.
- [#193](https://github.com/tobagin/karere/pull/193) remains open, but its production stylesheet was cherry-picked as `58e7e8d` and ships in 4.3.4. Its reviewed tools are integrated locally in `acceleration-upstream`.
- [#195](https://github.com/tobagin/karere/pull/195) remains a draft. Compatibility changes are published on the fork's `feat/vulkan-adaptive-refresh` branch.

The old `run-fixed.sh` now reports that it is retired. Its original executable
script is retained under `diagnostics/archive/`; old measurement binaries and
captures remain available.

## Remaining delivery gates for #195

1. Validate the conditional native-handle engine on the maintainer's AMD/Quadro
   hybrid and the RTX 5090, including default, explicit opt-in and missing-frame
   recovery. Validate the GTK-compatible Vulkan exports on hybrid hardware.
2. Keep the PR in draft while waiting for an official compatible CEF release,
   or agree on publishing a rebuilt conditional backport. Checked-in manifests
   still use the original engine; the previously tested local archive lacks
   the new switch.
3. Once engine artifacts are available, update the download URLs/checksums and
   rerun generated producer, presentation, media and recovery checks. Include
   physical 60/120 Hz and other-GPU coverage before claiming broad support.
4. Reconcile #193's open PR with its already-delivered production fix and the
   remaining diagnostic scope. No GitHub comments or PR state changes were made.

## Moving to another computer

All source branches are saved on [the GitHub fork](https://github.com/sknowledge1/karere).
The separate [migration backup branch](https://github.com/sknowledge1/karere/tree/backup/laptop-migration-2026-10-09/workspace-archive)
preserves the workspace reports, original diagnostic captures, measurement
binaries, validation logs and a Git bundle containing the source references.
Its `RESTORE.md` explains cloning, checking checksums and restoring the original
worktree layout. `manifest.json` records every archived file's size and SHA-256.
Regenerable Cargo caches, build intermediates and temporary test profiles are
excluded. GitHub authentication was verified through the desktop keyring;
the earlier sandbox-only login failure did not apply to publishing.

Current implementation and validation details are recorded in
[the compatibility report](acceleration-upstream/tools/scrolling-probe/COMPATIBILITY_VALIDATION.md).
Fresh checks passed: release build, strict release all-target Clippy, formatting,
113 Rust unit tests, both integration tests, generated Vulkan/GL ownership and
reuse checks, 49 Python regressions, JavaScript checks and both shell suites.
