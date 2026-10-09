#!/usr/bin/env bash
set -euo pipefail
echo 'This diagnostic launcher is retired; its scrolling fixes ship in Karere 4.3.4.' >&2
echo 'Launch the installed application with: flatpak run io.github.tobagin.karere' >&2
echo 'The original launcher is preserved in diagnostics/archive/run-fixed.sh.' >&2
exit 1
