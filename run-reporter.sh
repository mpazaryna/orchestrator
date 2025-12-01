#!/bin/bash
# Simple wrapper to run the reporter agent

cd "$(dirname "$0")"
uv run python orchestrator-v2.py
