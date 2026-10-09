**Current status, 9 October 2026:** stable 4.3.4 is now installed and includes the
wallpaper fix as upstream commit `58e7e8d`. #193 itself remains open. Original
v4.3.2 diagnostics are published in commit `2d7dd40`; reviewed tools are
also integrated in `acceleration-upstream`. The earlier application-restoration
statements below describe the September measurements, not the current install.
See [WORKSPACE_STATUS.md](WORKSPACE_STATUS.md) for current development status.

The follow-up investigation identified two separate conversation-scrolling costs:

- The large decorative SVG mask behind the conversation caused expensive raster work. Applying `will-change: transform` only to that background restored page updates from roughly 24 to 60 per second; reverting it restored the slowdown on both rendering paths.
- CPU frame delivery at this high-resolution viewport still missed some refreshes. With the background hint, window presentation reached roughly 55–56 frames/s on the CPU path and 60 on verified AMD DMA-BUF, with no presentation gaps over 25 ms in either repeated accelerated sample.

The user confirmed the final, stable **real WhatsApp conversation** felt **“Smooth and responsive”** with the temporary background hint and the original GPU preference (off).

The [full findings, methodology, limitations and fix proposal](conversation-upstream/tools/scrolling-probe/CONVERSATION_FINDINGS.md) include repeated original/change/change/original comparisons and separate page, draw and presentation measurements. [Aggregate measurements](conversation-upstream/tools/scrolling-probe/measurements/conversation_summary.json) and diagnostic tools are saved in the isolated v4.3.2 worktree.

The production wallpaper fix and evidence are now upstream in [PR #193](https://github.com/tobagin/karere/pull/193), with a [follow-up on issue #173](https://github.com/tobagin/karere/issues/173#issuecomment-5869735783). The clean implementation is in `wallpaper-upstream`, branch `fix/conversation-wallpaper-raster`, at `cc69b2fff8ac09331a64db06b0a98dc0ed2c986d`. The original diagnostic checkout remains available separately.

The [production validation report](wallpaper-upstream/tools/scrolling-probe/CONVERSATION_FINDINGS.md) records eight fresh stylesheet comparisons on current upstream and 16 passing browser DOM checks. Build, formatting, strict Clippy, `cargo check`, 96 Rust unit tests and the graphics-policy test passed. The existing GL-startup test failure was reproduced on unmodified upstream and documented in the PR.

The official application has been relaunched normally and the diagnostic listener is closed. GPU Rendering was off when captures started and enabled when final settings were checked; the current enabled preference was preserved. The installed Flatpak has not been replaced by the PR build, so it does not yet include the wallpaper fix.
