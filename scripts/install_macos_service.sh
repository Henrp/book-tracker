#!/bin/sh
# Installs a LaunchAgent that runs src/server.py in the background and
# starts it automatically on login, so you don't have to run it by hand.
set -e

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
PYTHON=$(command -v python3)
PLIST_NAME="com.book-tracker.server.plist"
DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

if [ -z "$PYTHON" ]; then
    echo "python3 not found on PATH" >&2
    exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents"

sed -e "s|__PYTHON__|$PYTHON|g" \
    -e "s|__REPO_DIR__|$REPO_DIR|g" \
    "$SCRIPT_DIR/com.book-tracker.plist.template" > "$DEST"

launchctl unload "$DEST" 2>/dev/null || true
launchctl load "$DEST"

echo "installed and started: $DEST"
echo "open http://127.0.0.1:5550 once it's running"
echo "to stop it: launchctl unload $DEST"
