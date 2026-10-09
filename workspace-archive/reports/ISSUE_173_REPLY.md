Following up with controlled measurements on **Karere 4.3.0**: I can reproduce a substantial frame-delivery stall on the **CPU-buffer off-screen rendering path**, while the page itself continues updating at about 60 times per second.

These new tests were on an AMD Radeon 680M / NVIDIA RTX 3050 Ti notebook running Aurora 44, KDE Wayland and the GNOME 50 Flatpak runtime. **AMD was the verified active GPU** (`GL_VENDOR=AMD`, successful DMA-BUF import in the accelerated runs). This is a different machine from my earlier desktop 5090 report; it demonstrates a software-path problem beyond NVIDIA, but does not validate NVIDIA acceleration or establish that every report here has the same cause.

The installed release was source commit `c8b3d71833d6b858f58b73f715aefec63ed98d14`, CEF `152.0.6+g708dc14` / Chromium `152.0.7977.83`. Display: 3840×2400 at 60 Hz, 190% desktop scale. All comparisons retained the same 4042×2346 OSR image, 2021×1173 CSS viewport and DPR 2.

**Actual WhatsApp chat-list comparison**

After startup settled, a probe moved `scrollTop` through the same 900 CSS-pixel range for 15 seconds, then restored its starting position. The sequence was CPU-buffer rendering → AMD GPU rendering → CPU-buffer rendering again, with the original 100 ms fallback timer throughout:

| Configuration | Page animation updates/s | CEF paint callbacks/s | GTK draw callbacks/s | CEF pump gap p95 |
| --- | ---: | ---: | ---: | ---: |
| GPU Rendering off | 60.00 | 19.87 | **10.00** | 100.46 ms |
| GPU Rendering on, AMD confirmed | 59.93 | 59.80 | **58.60** | 16.93 ms |
| GPU Rendering off again | 60.00 | 21.00 | **10.07** | 100.34 ms |

All three runs recorded actual scroll movement, a visible page and zero page long tasks. These are callback rates; compositor presentation FPS and input-to-screen latency were not measured. The probe collected timing and geometry without reading message/contact contents.

An interposer measured `cef_do_message_loop_work` entry/exit and `on_schedule_message_pump_work` with monotonic timestamps. Each CPU-path run contained **148 pump gaps longer than 50 ms, with no scheduling callbacks between pump executions across those gaps**. The four immediate requests that did arrive in each run were serviced in about 8 ms. In the initial CPU run, all 149 pump calls lasting at least 10 ms were followed by a gap over 50 ms; no pump call in the accelerated run lasted 10 ms.

Disabling Karere's rendering debug logs retained the same 148 long pump gaps and a 100.18 ms p95 interval, so rendering log overhead does not explain the pattern. I did not observe an urgent scheduling request being held behind a long pending timer.

**Independent control and relationship to the existing fix**

The problem also reproduced with generated scrolling rows in an isolated profile, without WhatsApp. Changing only the fallback from 100 ms to 8 ms raised drawing from **10.13 to 38.87 callbacks/s**; restoring 100 ms returned it to **10.00**. AMD GPU rendering with the original timer reached **59.73**. The 8 ms CPU-path experiment raised active process CPU use from about 70% to 135% of one core, so I would not propose permanent 8 ms polling as the fix.

The existing [v4.3.0 redraw change, 03d944a](https://github.com/tobagin/karere/commit/03d944a921c9a0b13bba36e664735ae8b0fd76cd), queues a GTK redraw directly from each CEF paint callback, avoiding the extra wait for the widget's 16 ms polling timer. **That change is already present in the tested release.** The new measurements show a remaining delay earlier in the pipeline, while CEF work/paint delivery waits for the [100 ms message-pump fallback](https://github.com/tobagin/karere/blob/v4.3.0/src/cef_runtime.rs#L379-L385).

A strong source-level lead is continuation scheduling when the [CEF external pump's 10 ms work slice ends](https://github.com/chromiumembedded/cef/blob/708dc14/libcef/browser/browser_message_loop.cc), alongside Karere's WorkSource-detachment patch from #151. The timing correlation supports investigating that exit path, but the exact CEF mechanism remains an inference: no rebuilt-CEF fix has been benchmarked. A patch should preserve timely pending-work continuations on the software path while retaining low idle/background CPU use; it should also be checked against both this generated workload and the actual chat-list workload.

Enabling GPU Rendering and fully restarting is a measured workaround on this notebook's **AMD** path. It is not a recommendation to bypass the NVIDIA compatibility check. Manual comparisons initially felt inconclusive, which is why I switched to the controlled reversal above. Native Preferences/menu lag remains a separate symptom that these measurements do not yet explain.
