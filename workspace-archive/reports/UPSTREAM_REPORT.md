**Current status, 9 October 2026:** #191 is merged, and the installed stable app
is 4.3.4. The historical reports below retain their original build provenance.
See [WORKSPACE_STATUS.md](WORKSPACE_STATUS.md) for current checkouts, #193's
cherry-picked production fix and #195's remaining engine/compatibility work.

**Draft issue: software OSR scrolling waits for the 100 ms CEF fallback; AMD DMA-BUF rendering avoids the stall**

Karere 4.3.0 reproducibly draws a scrolling page at about 10 callbacks/s on the CPU off-screen rendering path, even though the page's animation and scroll updates remain near 60/s. Enabling GPU Rendering on AMD restores about 60 paint/draw callbacks/s. This reproduces both on generated content in an isolated profile and on the actual WhatsApp chat list.

Environment: Karere source `c8b3d71833d6b858f58b73f715aefec63ed98d14`; CEF `152.0.6+g708dc14`, Chromium `152.0.7977.83`, including Karere's WorkSource-detachment patch; GNOME 50 Flatpak; Aurora 44/KDE Wayland; AMD Radeon 680M; 3840×2400/60 Hz panel at 190% desktop scale. Actual OSR image: 4042×2346; CSS viewport: 2021×1173; DPR: 2. Both CPU and GPU paths use the same geometry. AMD vendor and successful DMA-BUF import were verified.

The generated test animates `scrollTop` in a fixed pane containing generated rows for 15 seconds after a 5-second warmup. Each launch has an isolated temporary profile and memory-only preferences. Results:

| Rendering / fallback timer | Page animation/s | Paint callbacks/s | Draw callbacks/s | Pump gap p95 |
| --- | ---: | ---: | ---: | ---: |
| CPU / original 100 ms | 58.87 | 20.00 | 10.13 | 100.20 ms |
| CPU / temporary 8 ms | 59.47 | 59.27 | 38.87 | 15.78 ms |
| CPU / reverted 100 ms | 58.80 | 19.60 | 10.00 | 100.33 ms |
| AMD GPU / original 100 ms | 60.00 | 59.93 | 59.73 | 17.19 ms |

The actual WhatsApp chat list confirmed the preference reversal: **10.00 → 58.60 → 10.07 draw callbacks/s** with CPU → GPU → CPU, retaining the original 100 ms timer throughout. Each real-page run recorded zero long tasks, roughly 60 animation updates/s, and actual scroll movement.

An ABI-checked diagnostic interposer logged `cef_do_message_loop_work` entry/exit and `on_schedule_message_pump_work`. During each 15-second real CPU-path run there were 148 gaps over 50 ms, with **no scheduling callbacks between pump executions across those gaps**. Immediate requests that did arrive were serviced in about 8 ms. The long-pending-timer/coalescing hypothesis was not observed.

In the initial real-page CPU run, all 149 pump executions lasting at least 10 ms were followed by a gap over 50 ms; the accelerated run had no pump execution lasting 10 ms. Disabling Karere's rendering debug logs retained the same 148 long gaps and a 100.18 ms p95 pump interval.

The suspected mechanism is loss of timely continuation after CEF's 10 ms external-pump work slice is consumed. Inspect `MessagePumpExternal::Run` at CEF commit `708dc14`, including how the `DoWork()` next-work return value is handled on exit, together with Karere's WorkSource-detachment patch and 100 ms fallback. This mechanism remains a source-level inference; no rebuilt-CEF comparison has been performed.

The 8 ms override is a diagnostic control, not a proposed permanent fix: generated-page CPU usage rises from about 70% to 135% of one core while drawing still stays below 60/s. The existing GPU Rendering preference is the measured workaround on this AMD system.

Reproduction tools and instructions: [diagnostics/README.md](diagnostics/README.md). Aggregates: [automatic_summary.json](diagnostics/automatic_summary.json) and [chat_summary.json](diagnostics/chat_summary.json). The generated page allows reproduction without sharing account data. Callback rates are not compositor presentation FPS; manual wheel/touchpad and native-menu responsiveness remain separate validation targets.

An adapted version was [posted to issue #173](https://github.com/tobagin/karere/issues/173#issuecomment-5856247793). The exact published text is in [ISSUE_173_REPLY.md](ISSUE_173_REPLY.md).

[PR #191](https://github.com/tobagin/karere/pull/191) contributes the diagnostic tools, testing methodology and aggregate findings. A [follow-up comment](https://github.com/tobagin/karere/issues/173#issuecomment-5856319050) explains its scope and validation. The PR does not modify production rendering or claim a validated CEF scheduling fix. Its description is preserved in [PR_173_BODY.md](PR_173_BODY.md), and the checkout is in [upstream](upstream/).


The production fix is now published in PR #191 at commit dcc3c948d9de621521a60f171dfed9aee90e800f.
The final issue update is https://github.com/tobagin/karere/issues/173#issuecomment-5856702797.
See `upstream/tools/scrolling-probe/FIX_VALIDATION.md` for the compiled-build results.
