**Karere scrolling and UI lag: investigation plan**

Prepared 27 September 2026. This document preserves the original investigation plan and starting evidence. The executed comparisons, confirmed frame-delivery bottleneck and remaining limitations are in [PERFORMANCE_FINDINGS.md](PERFORMANCE_FINDINGS.md).

**Evidence collected**

| Item | Observation |
| --- | --- |
| Symptoms | Both mouse wheel and touchpad are affected. WhatsApp Web is smooth in the user's regular browser. |
| Installed application | Flathub stable, Karere 4.3.0, built 18 September 2026. Flatpak commit `32cc1d66019225336b91ab32909407110c5ddc5216a581df26a44b18f3c1f86e`. |
| Source matching the package | The installed manifest references tag object `a9e8300dec83d637ca3d8c536d410da31a9c21c5`, which resolves to source commit `c8b3d71833d6b858f58b73f715aefec63ed98d14` (`v4.3.0`). That source was inspected. |
| Rendering stack | GTK4/libadwaita with CEF 152.0.6 / Chromium 152.0.7977.83, using off-screen rendering into a GTK GLArea. Runtime: `org.gnome.Platform//50`; package sets `GSK_RENDERER=gl`. |
| Desktop | Aurora 44, KDE Wayland; kernel `7.1.10-200.fc44.x86_64`. |
| Display | Internal panel, 3840×2400 at 60 Hz, desktop scale 190%. |
| Graphics | AMD Radeon 680M plus NVIDIA RTX 3050 Ti Mobile. Host GLX diagnostic reports accelerated AMD rendering, Mesa 26.2.3. This does not establish which device Karere uses inside Flatpak. |
| Flatpak graphics | Mesa GL extension 26.2.2 is installed for the relevant runtime generation. NVIDIA driver and matching Flatpak extension are both `615.71.09`. No obvious missing device permission: the package grants `devices=all`. |
| Application preferences | `gpu-rendering=false`, `start-in-background=false`, `zoom-level=1.0`, `reduce-motion=false`. These are stored settings; live logs must confirm the path actually used. |
| System snapshot | On battery, platform profile `balanced`; about 6 GiB available memory and no CPU, memory, or I/O pressure in the sampled 10-second averages. This was not sampled during a controlled scrolling workload. |
| Running application | Initial Flatpak records referenced the installed 4.3.0 commit. No Karere instance appeared in the final process listing, so no live scrolling trace was captured. |

The [4.3.0 changelog](https://github.com/tobagin/karere/blob/v4.3.0/CHANGELOG.md) describes fixes to frame scheduling, while earlier releases fixed touchpad delta handling and added partial frame uploads. The matching source includes these changes. An old-version explanation is therefore a lower priority.

**Prioritized hypotheses**

| Priority | Hypothesis | Evidence and decisive comparison |
| --- | --- | --- |
| 1 | CPU frame copying/uploading is expensive at this display size. | GPU rendering is currently off. The CPU presentation path copies dirty image regions and uploads them to OpenGL. Compare CPU and accelerated presentation at identical window dimensions, recording actual backend and CPU/frame timing. |
| 2 | Scroll animation/input behavior differs from a normal browser. | The source explicitly adds `disable-smooth-scrolling`. Measure scroll distance, response delay, and frame gaps separately. If frames are timely but scrolling remains abrupt, compare an otherwise identical development build with that switch removed. |
| 3 | Fractional scaling, graphics selection, or Wayland presentation introduces stalls. | The panel uses 190% scaling and the notebook has two GPUs. Confirm the app's GPU and physical buffer size, then compare 190% and 200% at matched logical window dimensions. |
| 4 | WhatsApp page work or Karere integration blocks the UI thread. | Browser performance is good, but engines/profiles and injected integration code can differ. Compare native preferences, the embedded chat, and a synthetic scroll page; profile only the branch that reproduces the lag. |
| 5 | Battery power limits or a runtime/driver regression amplifies the problem. | Battery operation is confirmed; sustained throttling or driver trouble is not. Test power conditions separately and investigate runtime/driver differences only if earlier comparisons point there. |

**Investigation sequence**

1. **Establish a repeatable baseline.** Use one visible Karere instance and the same account, loaded conversation, window dimensions, zoom, display, and power condition for each run. Wait for startup/history loading to settle. Record 20 seconds idle, then 15 seconds each of wheel and touchpad scrolling. Repeat three times. Also compare chat-list scrolling, conversation scrolling, native Preferences scrolling, and typing in an unsent draft. Record the regular browser and version; if it is Firefox, add the already-installed Chrome as a closer engine comparison when needed.

   Record input-to-visible response, distance per wheel notch or comparable gesture, sustained frame cadence, long pauses, process/thread CPU, and memory pressure. A 60 Hz display has a 16.7 ms frame budget; a single frame-rate average can conceal long stalls. Use existing loaded content to avoid confusing history/network loading with rendering cost. Keep screenshot recording off when collecting page performance traces.

2. **Confirm the presentation path.** Fully quit through the app's Quit action before a diagnostic launch; closing its window may leave it in the background. Confirm its absence with `flatpak ps`. Capture a short startup/scroll log using module-scoped logging:

   ```sh
   flatpak run \
     --env=RUST_LOG=warn,karere::web_view=debug,karere::handlers::render=debug,karere::gl_dmabuf=info \
     io.github.tobagin.karere
   ```

   Look for `accel_osr: requested=… enabled=…`, GL context errors, `on_paint` versus `on_accelerated_paint`, `J4 draw … accel=…`, and actual frame dimensions. Check Karere/CEF GPU device handles or engine GPU diagnostics, rather than using host `glxinfo` as proof. Confirm whether 190% desktop scaling produces a 2× backing buffer in this GTK GLArea. Use verbose logs only for diagnosis, then repeat timings at normal logging levels. Existing log lines do not provide precise input-to-screen latency or frame IDs.

3. **Test rendering cost first.** Run a small matrix: GPU Rendering off/on × normal window/shorter window. Reduce height while keeping width fixed to avoid WhatsApp changing responsive layouts. Enable the preference through Preferences → General → Experimental → GPU Rendering and fully restart. Verify accelerated paint delivery; an enabled preference that falls back is not a valid GPU comparison. The preference respects Karere's NVIDIA compatibility check; avoid forcing `KARERE_GPU_OSR=1`, which bypasses that check. Restore the original setting after the comparison.

   A repeatable reduction in CPU use and frame stalls with acceleration, especially at larger dimensions, would implicate the CPU presentation path. Improvement from a smaller window alone identifies sensitivity to rendering workload but does not yet distinguish copying, painting, or compositing. If acceleration is rejected, retain the vendor/import failure evidence for the graphics branch.

4. **Separate fractional scaling and backend effects.** If the cause remains unclear, compare 190% with 200%, holding logical window dimensions and presentation mode constant; verify the backing-buffer dimensions in both cases. Restore 190% afterward. A material difference at similar buffer dimensions points toward fractional presentation. If necessary, make a separate one-run XWayland comparison with `flatpak run --socket=x11 --env=GDK_BACKEND=x11 io.github.tobagin.karere` after fully quitting. Keep `GSK_RENDERER=gl` fixed and check both GTK and CEF actually selected X11. The backend test also changes input handling, so interpret it alongside the distance/cadence measurements.

5. **Investigate scroll behavior if frame delivery is healthy.** Check wheel notch versus surface-unit classification, delta accumulation, scale conversion, and gesture momentum in `send_wheel`. Use a synthetic scroll page in an isolated development instance to compare scroll distance and timing with Chrome. Build two otherwise identical versions from the installed release source, changing only `disable-smooth-scrolling`; compare both devices. Treat improved interpolation as a scroll-behavior finding, not proof that unrelated typing/menu latency is fixed.

6. **Profile the remaining delay.** Use a short Sysprof capture of the relevant Karere/CEF processes during the reproducible workload. For page-specific stalls, collect a CEF/Chromium Performance trace and look for long JavaScript tasks, layout, and paint work. If the bottleneck remains between CEF and GTK, add monotonic timestamps and frame IDs around input forwarding, CEF paint callbacks, copy/upload, and GTK draw in a development build. Measure median/p95 latency, dropped/coalesced paints, damage area, and time spent copying or uploading. A GTK draw callback is not proof that the compositor has displayed the frame; use presentation feedback or a compositor trace when that distinction matters.

7. **Check secondary conditions and prove causality.** Compare battery and AC only after restoring the same graphics/display settings, recording the active power profile and CPU/GPU clocks. If a Flatpak/runtime regression remains plausible, compare controlled builds with the same Karere/CEF revision and explicit runtime versions. Preserve the production account data. Reproduce the original result, apply only the candidate change, then reverse it and repeat; identify any separate remaining symptoms.

**Completion criteria**

The result should name the responsible stage—input conversion/animation, CEF page execution, CPU copy/upload, GTK presentation, or compositor/driver—and include a repeatable before/after/reverted comparison. A setting that merely feels better is a useful workaround; a root-cause claim needs matching timing, CPU, or rendering-path evidence. Deliver the smallest supported configuration change or source patch, plus a concise upstream report if needed.

**Source locations for follow-up**

- [CEF switches, including smooth scrolling](https://github.com/tobagin/karere/blob/v4.3.0/src/cef_runtime.rs#L120-L142).
- [Frame-rate setting](https://github.com/tobagin/karere/blob/v4.3.0/src/web_view.rs#L1436-L1452), [GPU selection](https://github.com/tobagin/karere/blob/v4.3.0/src/web_view.rs#L2838-L2905), and [scroll delta conversion](https://github.com/tobagin/karere/blob/v4.3.0/src/web_view.rs#L3152-L3188).
- [CPU paint copying](https://github.com/tobagin/karere/blob/v4.3.0/src/handlers/render.rs#L128-L192), [redraw scheduling](https://github.com/tobagin/karere/blob/v4.3.0/src/handlers/render.rs#L297-L306), and [OpenGL upload/draw](https://github.com/tobagin/karere/blob/v4.3.0/src/web_view.rs#L1769-L1926).

No application settings, packages, display configuration, or source code were changed while preparing this plan. The version-matched source checkout is in `/tmp/karere-inspect.gI0P1n`; this document is the persistent workspace artifact.
