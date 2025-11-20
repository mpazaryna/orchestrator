#!/bin/bash
# Orchestrator tmux launcher
# Creates a persistent session for running multiple orchestrator tasks in parallel
# Each window can run --interactive to select and launch a skill

SESSION_NAME="orchestrator"
ORCHESTRATOR_DIR="/Users/mpaz/workspace/orchestrator"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}   🎯 Orchestrator - Multi-Window Execution${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"

# Check if session already exists
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo -e "${GREEN}✅ Session '$SESSION_NAME' already exists${NC}"
    echo -e "${YELLOW}Attaching...${NC}\n"
    tmux attach -t $SESSION_NAME
    exit 0
fi

echo -e "${BLUE}Creating new session: $SESSION_NAME${NC}\n"

# Create new session with dashboard window
tmux new-session -d -s $SESSION_NAME -n dashboard
cd "$ORCHESTRATOR_DIR"

# Setup dashboard window
tmux send-keys -t $SESSION_NAME:dashboard "clear" C-m
tmux send-keys -t $SESSION_NAME:dashboard "cat << 'EOF'
╔════════════════════════════════════════════════════════╗
║         🎯 ORCHESTRATOR - Multi-Window Control         ║
╚════════════════════════════════════════════════════════╝

QUICK START:
  1. Go to Window 1 or 2: Ctrl+b 1  (or Ctrl+b 2)
  2. Run: uv run python orchestrator.py --interactive
  3. Select skill → select repos → go!
  4. Watch Window 3 (Ctrl+b 3) for results

WINDOWS:
  Ctrl+b 0  →  Dashboard (this)
  Ctrl+b 1  →  Execution 1
  Ctrl+b 2  →  Execution 2
  Ctrl+b 3  →  Monitor results

CREATE MORE WINDOWS:
  Ctrl+b c  →  New window

NAVIGATION:
  Ctrl+b n  →  Next window
  Ctrl+b p  →  Previous window
  Ctrl+b d  →  Detach (keeps running)

REATTACH:
  tmux attach -t orchestrator

EOF" C-m

# Create first execution window
tmux new-window -t $SESSION_NAME: -n run-1
tmux send-keys -t $SESSION_NAME:run-1 "cd $ORCHESTRATOR_DIR && clear" C-m

# Create second execution window
tmux new-window -t $SESSION_NAME: -n run-2
tmux send-keys -t $SESSION_NAME:run-2 "cd $ORCHESTRATOR_DIR && clear" C-m

# Create monitor window
tmux new-window -t $SESSION_NAME: -n monitor
tmux send-keys -t $SESSION_NAME:monitor "cd $ORCHESTRATOR_DIR && clear && watch -n 2 'echo \"📊 Latest Results:\" && ls -lht ~/orchestrator_*_results.json 2>/dev/null | head -5 || echo \"Waiting for results...\"'" C-m

# Select dashboard window
tmux select-window -t $SESSION_NAME:dashboard

echo -e "\n${GREEN}✅ Session ready!${NC}"
echo -e "${YELLOW}Attaching now...${NC}\n"

tmux attach -t $SESSION_NAME
