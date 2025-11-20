# Global Orchestrator Shell Script

**Date**: 2025-11-20
**Type**: Feature Documentation
**Related Files**: `/usr/local/bin/orchestrator`, `tmux_interactive.sh`

## Overview

The global `orchestrator` shell script is a convenience wrapper that launches the orchestrator's tmux session from anywhere in your filesystem, without needing to navigate to the workspace directory.

## Motivation

When developing with the orchestrator, the typical workflow involves:
1. Opening a terminal
2. Navigating to `/Users/mpaz/workspace/orchestrator`
3. Running `./tmux_interactive.sh` to launch the orchestrator session

This required repetitive directory navigation. The global script eliminates this friction by making the orchestrator accessible from any location.

## Implementation

The script is installed at `/usr/local/bin/orchestrator` and contains:

```bash
#!/bin/bash
# Global orchestrator launcher
# Runs the tmux orchestrator from anywhere

ORCHESTRATOR_DIR="/Users/mpaz/workspace/orchestrator"

if [ ! -d "$ORCHESTRATOR_DIR" ]; then
    echo "❌ Error: Orchestrator directory not found at $ORCHESTRATOR_DIR"
    exit 1
fi

exec "$ORCHESTRATOR_DIR/tmux_interactive.sh"
```

## Usage

Run from any directory:

```bash
orchestrator
```

This is equivalent to:
```bash
cd /Users/mpaz/workspace/orchestrator
./tmux_interactive.sh
```

**Examples:**

```bash
# From home directory
cd ~
orchestrator

# From any project directory
cd ~/projects/my-app
orchestrator

# From the workspace root
cd /Users/mpaz/workspace
orchestrator
```

## Workflow Integration

The global script integrates seamlessly with the tmux orchestrator workflow:

1. **Launch orchestrator** from any terminal:
   ```bash
   orchestrator
   ```

2. **Tmux session opens** with 4 windows:
   - `dashboard` (Window 0): Instructions and quick start
   - `run-1` (Window 1): Execution window
   - `run-2` (Window 2): Parallel execution window
   - `monitor` (Window 3): Results monitoring

3. **Run interactive menu** in any execution window:
   ```bash
   uv run python orchestrator.py --interactive
   ```

4. **Select skills, repositories, and agents** via clean text-based menu

5. **Launch skill execution** across repositories

6. **Detach with `Ctrl+b d`** to keep session running (don't use `exit`)

## Session Management

### Attaching to existing session

If you run `orchestrator` when a session already exists:
```bash
$ orchestrator
✅ Session 'orchestrator' already exists
Attaching...
```

### Detaching vs. Exiting

**Correct way to exit** (use this!):
- Press `Ctrl+b d` to detach from the tmux session
- Session stays running in the background
- You can reconnect by running `orchestrator` again

**Wrong way to exit**:
- Typing `exit` in a window closes that window only
- The session persists but becomes partially broken
- Better to detach with `Ctrl+b d`

### Clean shutdown

To completely kill the orchestrator session:
```bash
tmux kill-session -t orchestrator
```

Then you can launch a fresh session with `orchestrator`.

## Available Commands

Within the orchestrator tmux session, you have access to orchestrator commands:

```bash
# Interactive skill/repo/agent selection
uv run python orchestrator.py --interactive

# List available skills
uv run python orchestrator.py --list-skills

# List configured repositories
uv run python orchestrator.py --list-repos

# List available agents
uv run python orchestrator.py --list-agents

# Run a specific skill on specific repos
uv run python orchestrator.py --skill project-moc-generator --repo-names authentic-advantage

# Run with a specific agent
uv run python orchestrator.py --skill project-moc-generator --repo-names authentic-advantage --agent research-agent
```

## Window Navigation

Within a tmux session created by `orchestrator`:

| Keyboard Shortcut | Action |
|---|---|
| `Ctrl+b 0` | Go to dashboard window |
| `Ctrl+b 1` | Go to run-1 window |
| `Ctrl+b 2` | Go to run-2 window |
| `Ctrl+b 3` | Go to monitor window |
| `Ctrl+b n` | Next window |
| `Ctrl+b p` | Previous window |
| `Ctrl+b c` | Create new window |
| `Ctrl+b d` | Detach (keep session running) |

## Typical Workflow Example

```bash
# From anywhere in your filesystem
$ orchestrator

# Tmux session launches with 4 windows
# In run-1 window, run the interactive menu:
$ uv run python orchestrator.py --interactive

# Menu appears:
# ────────────────────────────────────────────────────
#   SELECT SKILL
# ────────────────────────────────────────────────────
#
#    1. project-moc-generator      Generate project manifests
#    2. repo-summarizer            Summarize repository code
#    ... (more skills)
#
#   q. Cancel
#
# Select (1-12, q): 1

# Then select repositories, confirm, and skill runs
# Switch to monitor window (Ctrl+b 3) to watch results
# Run another skill in run-2 window (Ctrl+b 2) in parallel

# When done, detach with Ctrl+b d
# Session stays running, reconnect anytime with orchestrator
```

## Notes

- The script uses `exec` to replace the bash process with tmux, keeping process counts clean
- The orchestrator directory path is hardcoded and validated; if the directory doesn't exist, the script exits with an error message
- Supported from any terminal location thanks to placement in `/usr/local/bin`
- Complements the interactive menu system for guided skill/repo/agent selection
- Enables parallel execution workflows across multiple tmux windows
