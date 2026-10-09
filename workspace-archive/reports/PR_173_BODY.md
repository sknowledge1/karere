Karere's CPU-buffer rendering could animate the WhatsApp chat list at 60 updates/s while GTK drew it only about 10 times/s. This PR fixes the confirmed CEF frame-delivery stall investigated in #173. The final compiled fix delivered **59.53 GTK draws/s**, with GPU Rendering still off. Both original-executable control runs delivered **10.07 draws/s**.

CEF's bounded external pump can return with frame work pending without another scheduling callback. Karere then waited for its 100 ms fallback. The fix requests a continuation after accepting either a CPU or accelerated frame and schedules CEF below GTK input/redraw priority. Immediate work no longer waits an unconditional 8 ms.

Changes:

- One process-wide GLib source coalesces requests and the slow 100 ms idle backstop. Earlier deadlines replace later pending ones.
- Requests during CEF dispatch are deferred until it returns, preventing reentry. Stale dispatches are rejected and pending work is cancelled before CEF shutdown.
- Five scheduler regression tests cover continuation, request bursts, worker threads, native-event priority, idle backoff and shutdown.
- Reproducible generated-page and real chat-list tools, final aggregate measurements, compiled-binary and idle/background modes. The diagnostic timeout and empty-pump summary issues raised in review are also corrected.

Validation used the optimized executable inside the **same installed Flatpak runtime**, retaining its CEF library, AMD graphics stack and normal CPU-rendering preference. Geometry stayed at 4042×2346 backing pixels, 2021×1173 CSS pixels and DPR 2. The real list settled for 20 seconds, warmed for 5 seconds, then scrolled a fixed 900 CSS-pixel range for 15 seconds before restoring its offset. Only timing and geometry were collected; no messages or contacts were read or sent.

| Workload | Original GTK draws/s | Fixed GTK draws/s | Original → fixed pump gap p95 | Original → fixed idle CPU |
| --- | ---: | ---: | ---: | ---: |
| Generated CPU page | 10.07 | 59.33 | 100.21 → 10.00 ms | 0.7% → 0.7% |
| WhatsApp CPU chat list | 10.07 | 59.53 | 100.14 → 9.85 ms | 5.2% → 5.2% |

The final AMD DMA-BUF check delivered 59.87 draws/s. A separate close-to-background run verified hidden page visibility and 0.7% idle CPU. Idle samples lasted 30 seconds after 5 seconds settling; 100% CPU denotes one core. Active CPU use rises with the CPU path's roughly sixfold increase in drawing, from 72.4% to 123.6% for the real list. This is not a battery-life improvement claim.

All **98 repository tests passed**, including visible/background graphics startup and clean shutdown. Formatting and strict all-target Clippy checks passed, as did C probe compilation, Python checks, the CEF packaging consistency scripts and recomputation of all original aggregates. The optimized build retains an existing release-only dead-code warning in the render bridge.

[Full methodology, results and limitations](https://github.com/sknowledge1/karere/blob/diagnostics/cef-scroll-stalls-173/tools/scrolling-probe/FIX_VALIDATION.md). Callback rates are not compositor presentation FPS. Physical wheel/touchpad and perceived native-menu latency were not measured by the automatic workload. AMD acceleration was verified; NVIDIA acceleration remains unvalidated, so this does not claim to resolve the broader NVIDIA compatibility report.

Refs #173.
