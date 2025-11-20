# tmux Experiment

A simple tmux workflow to demonstrate multi-window orchestration.

## Quick Start

```bash
# Run the experiment
./tmux_experiment.sh

# Or with specific skill and group
./tmux_experiment.sh code-reviewer production
```

## What It Creates

The script creates a tmux session called `orchestrator-demo` with 4 windows:

### Window 0: Dashboard
Shows session info and instructions

### Window 1: Orchestrator
Ready to run the orchestrator command
- Press Enter to start the skill execution
- See live output as agents run

### Window 2: Monitor
Live watch of results files
- Auto-updates every 2 seconds
- Shows latest result files

### Window 3: Shell
General-purpose shell for:
- Checking repo status
- Running git commands
- Testing configurations

## tmux Commands

```bash
# Switch between windows
Ctrl+b 0    # Dashboard
Ctrl+b 1    # Orchestrator
Ctrl+b 2    # Monitor
Ctrl+b 3    # Shell

# Or use
Ctrl+b n    # Next window
Ctrl+b p    # Previous window

# Detach from session (keeps running in background)
Ctrl+b d

# Reattach later
tmux attach -t orchestrator-demo

# Kill session when done
tmux kill-session -t orchestrator-demo
```

## Usage Examples

### Example 1: Run on Development Group
```bash
./tmux_experiment.sh repo-summarizer development

# In orchestrator window, run:
uv run python orchestrator.py --skill repo-summarizer --group development
```

### Example 2: Run on Production Group
```bash
./tmux_experiment.sh code-reviewer production

# In orchestrator window, run:
uv run python orchestrator.py --skill code-reviewer --group production
```

### Example 3: Monitor Multiple Runs
```bash
# Start session
./tmux_experiment.sh

# Window 1 (orchestrator): Run first skill
uv run python orchestrator.py --skill repo-summarizer --group all

# Switch to Window 3 (shell): Start another in background
uv run python orchestrator.py --skill code-reviewer --repo-names mcp-fleet &

# Window 2 (monitor): Watch both running
```

## Next Steps

This experiment demonstrates the basics. Future enhancements:

1. **Auto-spawn agent windows**: Create one window per repository
2. **Split panes**: See multiple agents simultaneously
3. **Dashboard with status**: Real-time progress tracking
4. **Session persistence**: Save/restore sessions
5. **Human-in-the-loop**: Interactive approval gates

## Configuration-Based Workflows

Using `repos.json` config:

```bash
# List available repos
uv run python orchestrator.py --list-repos

# List groups
uv run python orchestrator.py --list-groups

# Run on specific repos by name
uv run python orchestrator.py --skill repo-summarizer --repo-names mcp-fleet rishi

# Run on group
uv run python orchestrator.py --skill repo-summarizer --group production

# Run on repos with tag
uv run python orchestrator.py --skill code-reviewer --tag ai
```

## Tips

1. **Detach Often**: Get in habit of `Ctrl+b d` to detach rather than closing
2. **Name Your Sessions**: For multiple projects, use different session names
3. **Use Split Panes**: `Ctrl+b "` (horizontal) or `Ctrl+b %` (vertical)
4. **Scroll Back**: `Ctrl+b [` then arrow keys, `q` to quit
5. **Copy Mode**: In scroll mode, `Space` to start selection, `Enter` to copy
