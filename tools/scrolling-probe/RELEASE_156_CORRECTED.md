# Corrected CEF 156 validation — 2 November 2026

**The tested NVIDIA build delivers 240-Hz-class fresh content:** all 18 selected
account samples pass ≥235 fresh presentations/s and p95 ≤8.33 ms. This evidence
applies to the frozen diagnostic build, not automatically to a later minimized PR.
Production delivery still needs a released CEF synchronization correction and
matching published codec artifacts.

[Per-sample numeric evidence](released-cef156-corrected-20261102.json) contains
18 selected samples for each build, capture-prefix hashes and the generated,
media, idle and functional controls. It excludes account contents, identifiers,
browser target IDs and profile paths.

## Scope and provenance

- Karere 4.3.4; released CEF 156.0.15 / Chromium 156.0.8078.80; bindings
  156.3.0+156.0.15; existing codec patches, no pending synchronization backport.
- RTX 5090, NVIDIA 615.78.08, Bazzite 44.20261026/kernel 7.2.11, KDE Wayland,
  GNOME Platform 51/GTK 4.24.1, 3840×2160 at 240 Hz, **125% scaling**, VRR Never.
- Candidate Flatpak `e74a6388a7707c2124b59d98da7ae843855c730e823609d7166c7badb07f4f77`.
  Bundle SHA-256 `5169833693c60069150678974a59253ee019d13b095b364b6376f548ac2a036d`;
  installed CEF SHA-256 `631eeb36f2450dd47c852775ceacdbbb86e2faa0d2b9eca3d3b425f2c1169a1c`.

**Earlier GTK/generated/account captures are excluded from isolated comparisons
and acceptance.** Flatpak reset reserved `XDG_*` launch variables, so those runs
used regular application directories. Corrected launches apply guarded roots
inside the sandbox and verify actual process environments and CEF directory
prefixes. Earlier untouched-account claims are withdrawn; no account rollback
was attempted. The [immutable probe/historical checkpoint](https://github.com/sknowledge1/karere/tree/762c9661bef6d562adf92eb142518069d584a47b/tools/scrolling-probe)
retains that audit and earlier measurements; the corrected results here supersede
its pending-status statements.

## Rendering results

Three 15-second samples per workload/size follow five seconds of active warmup.
Warmup or measurement layout changes invalidate an attempt; stable replacements
are retained separately. Viewports are 1859×944 and 3072×1636, DPR 2. Distinct CEF
content serials correlate with GTK commits and compositor feedback.

| Candidate workload | Size | Fresh/s, range | Median / p95 ms | CPU %, range |
|---|---|---:|---|---:|
| Selected chat, text range | Windowed | 237.067–239.467 | 4.167 / 4.193–4.195 | 135.0–140.0 |
| Selected chat, text range | Maximized | 238.267–239.533 | 4.166–4.167 / 4.186–4.214 | 123.9–128.9 |
| Chat list | Windowed | 236.600–236.733 | 4.167 / 4.198–4.200 | 90.8–92.6 |
| Chat list | Maximized | 236.333–236.800 | 4.167 / 4.187–4.192 | 106.2–108.9 |
| Selected chat, image-bearing range | Windowed | 238.800–239.333 | 4.167 / 4.194–4.199 | 134.4–138.4 |
| Selected chat, image-bearing range | Maximized | 236.600–239.400 | 4.167 / 4.189–4.194 | 130.0–134.5 |

No tolerance is applied to the minimum rate or maximum p95; 0.001-ms reporting
rounding cannot affect these comfortably passing values. CPU 100% is one logical
core. The observed path is Wayland, ANGLE OpenGL/EGL, GTK GL and owned GL texture
copies, requested/effective CEF rate 240, with zero CPU paints or discarded
presentation feedbacks in selected samples. No Vulkan preference is required.

Stock remains near 60 **window** presentations/s; fresh content is **presentation
unverified** because stock lacks serials. The instrumented original-CEF-152 CPU
control measures a **lower ceiling**, 44.133–230.267 fresh/s across its samples.
CPU recovery has no 235-FPS requirement. The candidate's second image-bearing
range stayed in the selected chat at the user's request; it differs from the
controls' separate media chat, so no matched media-chat speedup is claimed.

Twelve repeated generated GPU samples also pass (CEF GL/EGL or Vulkan, GTK GL).
Single selection controls favor GTK GL: GTK Vulkan falls to 68.2–68.4 fresh/s
maximized; CPU GL transfer reaches 82.333/s maximized and CPU snapshot 51.333/s.
Physical 60/119.88/240-Hz changes in the same browser produce 60.000/119.867/237.600
fresh/s; the runtime setter reports 60/120/240 and the desktop returns to 240 Hz.
Six Chrome controls reach 239.4–240.0 page callbacks/s; different geometry/DPR and
missing fresh-content correlation prevent a compositor-performance comparison.

## Functional, media and idle controls

- Generated image checks: three standalone producer paths each pass 72 resizes
  and 219 checked frames; five GTK paths each pass 72 resize transitions and 216
  checks, with no blank/partial output. This does not resolve the upstream race.
- H.264 playback and local WebRTC: eight cases, each three 30-second samples.
  VA-API decoding sustains 720p30/1080p60 and lowers playback CPU from
  11.7–12.5% to 7.5–8.5%, and 26.8–27.2% to 10.9–11.6%, respectively.
  Generated frame-grid comparisons match. These measure media callbacks, not
  compositor FPS. **Hardware encoding is unavailable:** both encoder-feature
  configurations use OpenH264. No actual WhatsApp call or screen sharing was tested.
- Strict generated idle: stock/candidate × visible/background × three 30-second
  samples after ten seconds settling. All twelve show zero paints/draws and no
  recovery. Mean CPU stock→candidate is 1.1931→1.1705% visible and 0.3747→0.3575%
  background, within observed sample variation. Restored candidate rendering
  reaches 239.467 fresh/s, median 4.167 ms, p95 4.185 ms.
- Original installed-schema controls verify absent preference→accelerated,
  saved false→CPU and persistent false after restart. The initial startup-check
  attempt remains excluded; its exact observation race was not established.
- Environment recovery, missing Vulkan at CEF/transfer layers, the ten-second
  missing-frame watchdog and one-launch X11 all pass. Invalid import metadata
  produces exactly one GL rejection, one Vulkan rejection and one CPU browser
  recreation. No real GPU reset/hang/device loss was induced.
- CPU/GPU popup controls pass both ordinary and edge-position CEF lifecycle and
  selection checks. They do not establish GTK popup pixels, placement or colors.
  Fault/observer captures are never performance samples.

Final cleanup passes: diagnostics/listeners closed, temporary scripts unloaded,
app-specific user/system overrides empty and normal Devel relaunched with its
normal roots. The existing global system override predates the retest and matches
between cleanup audits; there is no original global-content snapshot. Display
settings are unchanged. The account index matched the preserved discovery state
before relaunch and changed afterward, which may be normal activity; this is not
an unchanged-all-account-data claim.

## Remaining production gates

The original NVIDIA allocation fix is released. The later completion-wait change
[landed on Chromium main](https://chromium-review.googlesource.com/c/chromium/src/+/8589742),
but is absent from frozen Chromium 156.0.8078.80;
[CEF #4314](https://github.com/chromiumembedded/cef/pull/4314) remains open as checked
2 November. Wait for a released CEF containing it, then rerun ownership/image,
recovery and presentation checks. No release date is established.

The newest [published Karere codec artifacts](https://github.com/tobagin/karere/releases/tag/cef-152.0.6-proprietary-codecs)
are still CEF 152.0.6. Production engine/binding pins need matching x86_64 and
ARM64 artifacts. Wider GPU/hybrid hardware, final-build 145% scaling, physical
wheel/touchpad quality and GTK popup visuals remain unverified. A reply of “done”
does not establish those observations. Hardware encoding and real calls remain
explicitly unsupported/unverified through this test stack.

## Reproduce the guarded account capture

Use the immutable [probe README](https://github.com/sknowledge1/karere/blob/762c9661bef6d562adf92eb142518069d584a47b/tools/scrolling-probe/README.md)
and matching-CEF instrumentation. Stop Devel normally before making a private,
marked cold clone outside regular Flatpak profiles; use that clone only and never
reopen a CEF-156-upgraded copy with CEF 152. The application must match the tested
engine/binary identities; checking out the probe commit does not install it.

Set `PRIVATE_PROFILE` to that existing guarded clone, choose unused `CAPTURE`
and `SAMPLE` labels, and set `ANCHOR_BOTTOM` to a safe, fixed, fully loaded range.
In one terminal:

```sh
KARERE_PROBE_CDP=1 python3 tools/scrolling-probe/karere_probe.py "$CAPTURE" \
  --app-id io.github.tobagin.karere.Devel \
  --profile-directory "$PRIVATE_PROFILE" --profile-transfer accelerated \
  --windowed --schedule-probe --wayland-timing
```

With one visible selected conversation, in a second terminal:

```sh
for n in 1 2 3; do
  python3 tools/scrolling-probe/conversation_probe.py "${SAMPLE}_${n}" \
    --target conversation --duration 15 --amplitude 900 \
    --anchor-bottom "$ANCHOR_BOTTOM"
done
```

The probe supplies five seconds of active warmup. Repeat at the matched maximized
size; use `--target list --amplitude 600` for the list and preserve its absolute
sweep base across different loaded heights. Reject interruptions, changing
warmup/active scroll height, target/geometry changes and ambiguous presentation.
Keep three valid samples per size and preserve rejected attempts. Quit the owned
diagnostic app normally before final analysis:

```sh
python3 tools/scrolling-probe/presentation_report.py \
  "tools/scrolling-probe/results/${CAPTURE}.jsonl" \
  --page "tools/scrolling-probe/results/${SAMPLE}_1_page.json" \
  --page "tools/scrolling-probe/results/${SAMPLE}_2_page.json" \
  --page "tools/scrolling-probe/results/${SAMPLE}_3_page.json" --single-view
```

The original reporter alone does not reject every warmup-only layout change;
compare the initial geometry with active frame heights before selecting samples.
The corrected batch additionally checks that invariant and snapshots complete
JSONL prefixes, preserving startup clocks/serial history. Its source/parity hashes
and per-sample outcomes are in the numeric evidence. Restore original scroll and
window state and verify listeners are closed. Programmatic input tests capacity,
not physical wheel/touchpad behavior.

Account capture-prefix SHA-256 values (raw captures retained privately):

| Build | SHA-256 |
|---|---|
| Stock 4.3.4 | `026b92f47203f81a34d26fa49f410f4b58cd78a2834954997c3d371c9e062b63` |
| PR / CEF 152 CPU | `23b8f5650b2eefbef35eee0ba1aead2189cd199131246d845984571087c4a0b2` |
| CEF 156 accelerated | `7158284bd3eb9995945d3725b284552e2b73b24df8b1c8b5dc8afa4127d623c4` |
