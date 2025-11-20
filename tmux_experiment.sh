#!/bin/bash
# Simple tmux experiment for orchestrator
# This script creates a tmux session with multiple windows for monitoring agents

SESSION_NAME="orchestrator-demo"
SKILL="${1:-repo-summarizer}"
GROUP="${2:-development}"

echo "Creating tmux session: $SESSION_NAME"
echo "Skill: $SKILL"
echo "Group: $GROUP"
echo ""

# Check if session already exists
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? == 0 ]; then
    echo "Session '$SESSION_NAME' already exists. Attaching..."
    tmux attach -t $SESSION_NAME
    exit 0
fi

# Create new session with dashboard window
echo "Creating new session..."
tmux new-session -d -s $SESSION_NAME -n dashboard

# Setup dashboard window
tmux send-keys -t $SESSION_NAME:dashboard "echo '=== Orchestrator Dashboard ==='" C-m
tmux send-keys -t $SESSION_NAME:dashboard "echo 'Session: $SESSION_NAME'" C-m
tmux send-keys -t $SESSION_NAME:dashboard "echo 'Skill: $SKILL'" C-m
tmux send-keys -t $SESSION_NAME:dashboard "echo 'Group: $GROUP'" C-m
tmux send-keys -t $SESSION_NAME:dashboard "echo ''" C-m
tmux send-keys -t $SESSION_NAME:dashboard "echo 'Windows:'" C-m
tmux send-keys -t $SESSION_NAME:dashboard "echo '  0: dashboard (this window)'" C-m
tmux send-keys -t $SESSION_NAME:dashboard "echo '  1: orchestrator (running skill)'" C-m
tmux send-keys -t $SESSION_NAME:dashboard "echo '  2: monitor (watch results)'" C-m
tmux send-keys -t $SESSION_NAME:dashboard "echo '  3: shell (for commands)'" C-m
tmux send-keys -t $SESSION_NAME:dashboard "echo ''" C-m
tmux send-keys -t $SESSION_NAME:dashboard "echo 'Switch windows: Ctrl+b [0-3]'" C-m
tmux send-keys -t $SESSION_NAME:dashboard "echo 'Detach: Ctrl+b d'" C-m
tmux send-keys -t $SESSION_NAME:dashboard "echo 'Kill session: tmux kill-session -t $SESSION_NAME'" C-m

# Create orchestrator window
tmux new-window -t $SESSION_NAME: -n orchestrator
tmux send-keys -t $SESSION_NAME:orchestrator "cd /Users/mpaz/workspace/orchestrator" C-m
tmux send-keys -t $SESSION_NAME:orchestrator "echo 'Running orchestrator with skill: $SKILL on group: $GROUP'" C-m
tmux send-keys -t $SESSION_NAME:orchestrator "echo 'Press Enter to start...'" C-m
# Don't auto-start, wait for user
# tmux send-keys -t $SESSION_NAME:orchestrator "uv run python orchestrator.py --skill $SKILL --group $GROUP" C-m

# Create monitor window
tmux new-window -t $SESSION_NAME: -n monitor
tmux send-keys -t $SESSION_NAME:monitor "cd /Users/mpaz/workspace/orchestrator" C-m
tmux send-keys -t $SESSION_NAME:monitor "echo '=== Results Monitor ==='" C-m
tmux send-keys -t $SESSION_NAME:monitor "echo 'Watching for results...'" C-m
tmux send-keys -t $SESSION_NAME:monitor "watch -n 2 'ls -lht ~/orchestrator_*_results.json 2>/dev/null | head -5'" C-m

# Create shell window
tmux new-window -t $SESSION_NAME: -n shell
tmux send-keys -t $SESSION_NAME:monitor "cd /Users/mpaz/workspace/orchestrator" C-m

# Go back to dashboard
tmux select-window -t $SESSION_NAME:dashboard

# Attach to session
echo ""
echo "Session created! Attaching..."
tmux attach -t $SESSION_NAME
