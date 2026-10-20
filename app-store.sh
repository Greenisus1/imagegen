#!/bin/bash
# pi-app-store: 1
# pi-app-store-category: tools
# pi-app-store-description: AI image generator. Type a description, puter.js draws it free in your browser (a free Puter sign-in is needed), and one click saves the picture onto the Pi. Nothing to install.
set -eu
cd -- "$(dirname -- "$0")"
case "${1:-}" in
 install) mkdir -p images; python3 -c 'from pathlib import Path;[compile(p.read_bytes(),str(p),"exec") for p in Path(".").glob("*.py")]' ;;
 run) shift; exec python3 imagegen.py "$@" ;;
 *) echo 'Use: bash app-store.sh install OR bash app-store.sh run';exit 1 ;;
esac
