PR #191 now contains a tested application fix for the frame-delivery stall, alongside the reproducer and findings.

The problem was CEF work waiting for Karere's 100 ms fallback after a bounded work slice returned without another scheduling notification. The fix requests a continuation after frame delivery on both CPU and accelerated paths. A single scheduler coalesces requests, honors earlier deadlines, lets GTK input/redraw run first, prevents reentry, and retains the slow idle backstop.

Tests used the compiled executable inside the same installed Flatpak runtime, with the same maximized geometry and **GPU Rendering off**:

| Real WhatsApp chat list | GTK draw callbacks/s | CEF pump gap p95 |
| --- | ---: | ---: |
| Original executable | 10.07 | 100.14 ms |
| Fixed executable | 59.53 | 9.85 ms |
| Original executable restored | 10.07 | 100.16 ms |

Each real-page run used a 20-second settle, 5-second warmup and fixed 15-second scroll, then restored the starting offset. It collected timing/geometry without reading or sending messages. Generated content independently reproduced the improvement. Settled idle CPU was 5.2% of one core for both original and fixed real-page runs; a verified hidden-background test used 0.7%. Active CPU rose from 72.4% to 123.6% while delivering almost six times as many draws. The AMD GPU path also remained near 60 draws/s.

All 98 repository tests, formatting and strict Clippy checks passed. [The PR's validation report](https://github.com/sknowledge1/karere/blob/diagnostics/cef-scroll-stalls-173/tools/scrolling-probe/FIX_VALIDATION.md) includes the methodology, exact measurements, source explanation and limitations.

This addresses the confirmed CEF scheduling stall. These are draw-callback counts, not measured display FPS; NVIDIA acceleration and the separately reported native-menu latency are not claimed fixed. The official Flatpak will need an upstream release containing the change.
