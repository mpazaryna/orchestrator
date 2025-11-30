#!/bin/bash
# Claude Code Multi-Project Launcher (Zellij)
# Usage: ./claude_code.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LAYOUT_FILE="$SCRIPT_DIR/claude_code.kdl"

# Check if zellij is installed
if ! command -v zellij &> /dev/null; then
    echo "Zellij not found. Install with: brew install zellij"
    exit 1
fi

zellij --layout "$LAYOUT_FILE"
