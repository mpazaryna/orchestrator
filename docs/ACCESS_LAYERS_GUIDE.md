# Orchestrator Access Layers Guide

**For Teams**: How to interact with the orchestrator agent system across different modalities.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Access Layer 1: Command Line Interface (CLI)](#access-layer-1-command-line-interface-cli)
4. [Access Layer 2: MCP Server](#access-layer-2-mcp-server)
5. [Access Layer 3: Interactive Menu](#access-layer-3-interactive-menu)
6. [Access Layer 4: tmux Workflows](#access-layer-4-tmux-workflows)
7. [Agent Types](#agent-types)
8. [Common Workflows](#common-workflows)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The orchestrator provides **multiple ways** to access the same underlying agent system. Think of it like accessing your email - you can use a desktop app, web browser, mobile app, or command line. Same data, different interfaces.

**Why multiple access layers?**
- **CLI**: Automation, scripts, cron jobs
- **MCP Server**: Natural language from Claude Code, cross-project access
- **Interactive Menu**: Discovery, batch operations
- **tmux**: Parallel workflows, persistent sessions

All access layers use the same:
- Agent registry (`config/agents.json`)
- Skill registry (`config/skills.json`)
- Repository registry (`config/repos.json`)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ACCESS LAYERS                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   CLI    │  │   MCP    │  │   Menu   │  │   tmux   │        │
│  │          │  │  Server  │  │Interactive│  │ Windows  │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
└───────┼─────────────┼─────────────┼─────────────┼───────────────┘
        │             │             │             │
        └─────────────┴──────┬──────┴─────────────┘
                             │
┌────────────────────────────┴──────────────────────────────────────┐
│                    ORCHESTRATOR CORE                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Config      │  │   Python     │  │  Autonomous  │           │
│  │  Loader      │  │   Agent      │  │   Agent      │           │
│  │              │  │   Runner     │  │   Runner     │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└────────────────────────────┬──────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────┴───────┐    ┌───────┴───────┐    ┌──────┴──────┐
│ Python Agents │    │  Autonomous   │    │   Skills    │
│               │    │   Agents      │    │             │
│ synth-notes   │    │  research     │    │ repo-summ   │
│ github-pm     │    │  quality-ctrl │    │ moc-gen     │
└───────────────┘    └───────────────┘    └─────────────┘
```

---

## Access Layer 1: Command Line Interface (CLI)

### When to Use
- Scripting and automation
- CI/CD pipelines
- Cron jobs
- Quick one-off commands
- SSH remote execution

### Setup

```bash
cd /path/to/orchestrator
source .venv/bin/activate  # or use uv run
```

### Running Python Agents

**List available agents:**
```bash
uv run python -m orchestrator --list-agents
```

**Run synth-notes-generator:**
```bash
# Generate 5 adult neck pain SOAP notes
uv run python -m orchestrator \
  --run-agent synth-notes-generator \
  --prompt-type adult_neck_pain \
  --total 5 \
  --batch-size 2
```

**Run github-pm-analyzer:**
```bash
# Get last 7 days of commit activity
uv run python -m orchestrator \
  --run-agent github-pm-analyzer \
  --task daily_activity \
  --days 7

# List available issue snapshots
uv run python -m orchestrator \
  --run-agent github-pm-analyzer \
  --task list_snapshots

# Compare two snapshots for trends
uv run python -m orchestrator \
  --run-agent github-pm-analyzer \
  --task trend_analysis \
  --baseline 2025-11-15_09-00 \
  --current 2025-11-21_09-00
```

### Running Skills Across Repositories

**List skills:**
```bash
uv run python -m orchestrator --list-skills
```

**Run a skill on specific repos:**
```bash
# Run repo-summarizer on multiple repos
uv run python -m orchestrator \
  --skill repo-summarizer \
  --repo-names orchestrator claude-toolkit synthetic-notes
```

**Run a skill on a group:**
```bash
# Run on all repos tagged 'active'
uv run python -m orchestrator \
  --skill repo-summarizer \
  --tag active
```

### Interactive Mode

Launch the interactive menu from CLI:
```bash
uv run python -m orchestrator --interactive
```

### Full CLI Options

```bash
uv run python -m orchestrator --help

Options:
  --list-agents         List all configured agents
  --list-skills         List all configured skills
  --list-repos          List all repositories
  --list-groups         List repository groups

  --run-agent AGENT     Run a Python agent
  --task TASK           Task for Python agent
  --prompt-type TYPE    For synth-notes
  --total N             For synth-notes
  --batch-size N        For synth-notes
  --days N              For github-pm

  --skill SKILL         Run a skill
  --repos PATH [PATH..] Direct repo paths
  --repo-names [NAMES]  Repo names from config
  --group GROUP         Run on group
  --tag TAG             Run on tagged repos

  --interactive         Interactive menu mode
  --agent/-a            Use autonomous agent mode (default)
  --simple              Use simple prompt mode
```

---

## Access Layer 2: MCP Server

### When to Use
- Natural language interaction
- Cross-project work (access from any repo)
- Ad-hoc requests
- Working in Claude Code
- Exploring capabilities

### Setup

**1. Configure MCP in orchestrator:**

File: `/path/to/orchestrator/.mcp.json`
```json
{
  "mcpServers": {
    "orchestrator": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "python", "src/mcp/server.py"],
      "cwd": "/Users/yourname/workspace/orchestrator",
      "env": {}
    }
  }
}
```

**2. Link to Claude Code globally (optional):**

```bash
# Link to global Claude Code settings
ln -s /path/to/orchestrator/.mcp.json ~/.config/claude/mcp.json

# Or copy to specific repo
cp /path/to/orchestrator/.mcp.json /path/to/other-repo/.mcp.json
```

**3. Restart Claude Code**

The MCP server will auto-start when tools are called.

### Usage in Claude Code

The MCP server exposes agents as natural language tools:

**Available Tools:**

1. **`list_agents`** - List all agents
2. **`generate_soap_notes`** - Generate clinical SOAP notes
3. **`list_soap_prompt_types`** - List available note types
4. **`analyze_issue_trends`** - Compare GitHub issue snapshots
5. **`get_daily_activity`** - Analyze commit activity
6. **`sync_github_repos`** - Sync/filter GitHub repos
7. **`list_issue_snapshots`** - List available snapshots

**Example Prompts:**

```
"List my agents"

"Generate 10 adult neck pain SOAP notes"

"Show my GitHub activity for the last 14 days"

"List available issue snapshots"

"Analyze trends between snapshot A and snapshot B"

"What SOAP note types are available?"
```

### MCP Server Architecture

```
┌──────────────────────────────────────────────┐
│         Claude Code (any repo)               │
│  "generate 5 SOAP notes"                     │
└────────────────┬─────────────────────────────┘
                 │ MCP Protocol
┌────────────────┴─────────────────────────────┐
│         MCP Server (src/mcp/server.py)       │
│  ┌────────────────────────────────────────┐  │
│  │  Core Tools:                           │  │
│  │  - list_agents()                       │  │
│  │  - list_skills()                       │  │
│  └────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────┐  │
│  │  Tool Modules:                         │  │
│  │  - synth_notes/                        │  │
│  │  - github_pm/                          │  │
│  └────────────────────────────────────────┘  │
└────────────────┬─────────────────────────────┘
                 │
┌────────────────┴─────────────────────────────┐
│      Python Agent Runner                     │
│  Dynamically loads and executes agents       │
└──────────────────────────────────────────────┘
```

**Adding New Tools:**

Create a new module in `src/mcp/tools/`:

```python
# src/mcp/tools/my_tool/__init__.py
from .analysis import register_tools
__all__ = ['register_tools']

# src/mcp/tools/my_tool/analysis.py
def register_tools(mcp, config_loader, python_runner):
    @mcp.tool()
    def my_tool_function(param: str) -> dict:
        """Tool description."""
        agent_config = config_loader.get_agent("my-agent")
        return python_runner.run_agent(
            agent_config=agent_config.__dict__,
            task_config={"param": param}
        )
```

Register in `src/mcp/server.py`:
```python
from tools.my_tool import register_tools as register_my_tool
register_my_tool(mcp, config_loader, python_runner)
```

---

## Access Layer 3: Interactive Menu

### When to Use
- Discovering what's available
- Batch operations on multiple repos
- Visual selection vs typing commands
- Training new team members
- Exploring agent capabilities

### Launch

```bash
uv run python -m orchestrator --interactive
```

### Menu Structure

```
┌──────────────────────────────────────┐
│   Orchestrator Interactive Menu      │
├──────────────────────────────────────┤
│ 1. Select Skill                      │
│    ├─ repo-summarizer                │
│    ├─ moc-generator                  │
│    └─ quality-checker                │
│                                      │
│ 2. Select Repositories               │
│    ├─ orchestrator                   │
│    ├─ claude-toolkit                 │
│    ├─ synthetic-notes                │
│    └─ ... (multi-select)             │
│                                      │
│ 3. Execute                           │
│    Run selected skill on N repos     │
└──────────────────────────────────────┘
```

### Workflow

1. **Select a skill** from the list
2. **Select repositories** (multi-select with spacebar)
3. **Confirm and execute**
4. **View progress** and results
5. Results saved to `~/orchestrator_[skill]_results.json`

### Batch Operations Example

```bash
# Launch menu
uv run python -m orchestrator --interactive

# In menu:
# 1. Select "repo-summarizer"
# 2. Select 5 repositories
# 3. Execute
# → Generates PROJECT.md for all 5 repos in parallel
```

---

## Access Layer 4: tmux Workflows

### When to Use
- Running multiple agents in parallel
- Long-running operations
- Persistent sessions (detach/reattach)
- Monitoring multiple outputs
- Remote server workflows

### Setup tmux Session

**Create orchestrator session:**

```bash
# Start new session
tmux new -s orchestrator

# Create windows
tmux new-window -n mcp-server    # Window 0: MCP server
tmux new-window -n agents        # Window 1: Run agents
tmux new-window -n monitor       # Window 2: Monitor logs
```

### Persistent MCP Server

**Window 0: MCP Server**
```bash
cd /path/to/orchestrator
uv run python src/mcp/server.py
# Server runs persistently, restart only when updating
```

### Parallel Agent Execution

**Window 1: Run Agents**
```bash
# Split panes for parallel work
tmux split-window -h
tmux split-window -v

# Pane 1: Generate SOAP notes
uv run python -m orchestrator \
  --run-agent synth-notes-generator \
  --prompt-type adult_trauma --total 20

# Pane 2: Analyze GitHub activity
uv run python -m orchestrator \
  --run-agent github-pm-analyzer \
  --task daily_activity --days 30

# Pane 3: Run skill across repos
uv run python -m orchestrator \
  --skill repo-summarizer --tag active
```

### Monitoring

**Window 2: Monitor**
```bash
# Watch for new SOAP notes
watch -n 2 'ls -lth ~/workspace/synthetic-notes/output/batch_*/note_*.json | head'

# Monitor orchestrator results
tail -f ~/orchestrator_*.json
```

### tmux Session Management

```bash
# List sessions
tmux ls

# Attach to session
tmux attach -t orchestrator

# Detach (keep running)
Ctrl+b d

# Switch windows
Ctrl+b 0  # Window 0 (MCP)
Ctrl+b 1  # Window 1 (Agents)
Ctrl+b 2  # Window 2 (Monitor)

# Kill session
tmux kill-session -t orchestrator
```

### Example tmux Layout

```
┌─────────────────────────────────────────────────────────────┐
│ [0:mcp-server] [1:agents*] [2:monitor]                      │
├─────────────────────┬───────────────────────────────────────┤
│                     │                                       │
│  SOAP Notes Gen     │    GitHub PM Analyzer                │
│  Batch: 006         │    Analyzing 34 repos...             │
│  Progress: 8/20     │    Commits: 156                      │
│  Cost: $0.45        │    Period: 30 days                   │
│                     │                                       │
├─────────────────────┴───────────────────────────────────────┤
│  Repo Summarizer                                            │
│  Processing: claude-toolkit (3/5)                          │
│  Files created: PROJECT.md                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent Types

### Python Agents (`type: "python"`)

**Characteristics:**
- Self-contained Python classes
- Direct API access
- Return structured JSON results
- No Claude Code tool-use loop
- Fully autonomous

**Current Python Agents:**

**1. synth-notes-generator**
```bash
# CLI
uv run python -m orchestrator \
  --run-agent synth-notes-generator \
  --prompt-type adult_neck_pain --total 10

# MCP
"generate 10 adult neck pain SOAP notes"
```

**2. github-pm-analyzer**
```bash
# CLI - Daily activity
uv run python -m orchestrator \
  --run-agent github-pm-analyzer \
  --task daily_activity --days 7

# CLI - Trend analysis
uv run python -m orchestrator \
  --run-agent github-pm-analyzer \
  --task trend_analysis \
  --baseline 2025-11-15_09-00 \
  --current 2025-11-21_09-00

# MCP
"show my GitHub activity for the last 14 days"
"analyze issue trends between snapshot A and B"
```

### Autonomous Agents (`type: "autonomous"`)

**Characteristics:**
- Use Claude's tool-use loop
- Tools: read_file, write_file, run_bash, search_files, list_files
- Iterative problem-solving
- Context-aware file operations

**Current Autonomous Agents:**

1. **research-agent** - Web research and documentation gathering
2. **research-docs-fetcher** - Fetch and organize documentation
3. **quality-control-enforcer** - Quality validation and reporting
4. **work-completion-summarizer** - Generate work summaries

**Usage:**
```bash
# Via skills (autonomous agents run through skill interface)
uv run python -m orchestrator \
  --skill research-deep-dive \
  --repos /path/to/repo
```

### Skills

**Characteristics:**
- Markdown templates (SKILL.md)
- Can invoke autonomous agents
- Work across multiple repositories
- Template-driven output

**Current Skills:**

1. **repo-summarizer** - Generate PROJECT.md for repos
2. **moc-generator** - Create Map of Content docs
3. **synth-notes** - SOAP notes via Python agent

**Usage:**
```bash
# Run on specific repos
uv run python -m orchestrator \
  --skill repo-summarizer \
  --repo-names orchestrator claude-toolkit

# Run on all active repos
uv run python -m orchestrator \
  --skill repo-summarizer \
  --tag active
```

---

## Common Workflows

### Workflow 1: Daily Development Standup

**Goal:** Generate daily activity report across all repos

**Access Layer:** CLI (cron job)

```bash
#!/bin/bash
# Save as: daily-standup.sh
# Cron: 0 9 * * * /path/to/daily-standup.sh

uv run python -m orchestrator \
  --run-agent github-pm-analyzer \
  --task daily_activity \
  --days 1 \
  > ~/standup-$(date +%Y-%m-%d).txt

# Email results
mail -s "Daily Standup $(date +%Y-%m-%d)" team@company.com \
  < ~/standup-$(date +%Y-%m-%d).txt
```

### Workflow 2: Generate Training Data

**Goal:** Generate 100 synthetic SOAP notes for model training

**Access Layer:** tmux (monitor progress)

```bash
# Window 1: Run generator
uv run python -m orchestrator \
  --run-agent synth-notes-generator \
  --prompt-type adult_neck_pain \
  --total 100 \
  --batch-size 5

# Window 2: Monitor
watch -n 5 'ls -lh ~/workspace/synthetic-notes/output/batch_*/*.json | wc -l'
```

### Workflow 3: Multi-Repo Documentation Update

**Goal:** Update PROJECT.md for all active repositories

**Access Layer:** Interactive Menu

```bash
uv run python -m orchestrator --interactive

# In menu:
# 1. Select "repo-summarizer"
# 2. Select all active repos (spacebar to multi-select)
# 3. Execute
# Results: ~/orchestrator_repo-summarizer_results.json
```

### Workflow 4: Issue Trend Analysis

**Goal:** Weekly trend analysis of GitHub issues

**Access Layer:** MCP Server (natural language)

From Claude Code:
```
"List my issue snapshots"
"Analyze trends between 2025-11-14_09-00 and 2025-11-21_09-00"
"Summarize the key insights from the trend analysis"
```

### Workflow 5: Parallel Agent Army

**Goal:** Run multiple agents across multiple repos simultaneously

**Access Layer:** tmux with multiple panes

```bash
# Create 4-pane layout
tmux split-window -h
tmux split-window -v
tmux select-pane -t 0
tmux split-window -v

# Pane 0: SOAP notes - adult trauma
uv run python -m orchestrator \
  --run-agent synth-notes-generator \
  --prompt-type adult_trauma --total 50

# Pane 1: SOAP notes - pediatric
uv run python -m orchestrator \
  --run-agent synth-notes-generator \
  --prompt-type torticollis --total 50

# Pane 2: GitHub analysis
uv run python -m orchestrator \
  --run-agent github-pm-analyzer \
  --task daily_activity --days 30

# Pane 3: Repo summaries
uv run python -m orchestrator \
  --skill repo-summarizer --tag active
```

---

## Troubleshooting

### MCP Server Not Connecting

**Symptom:** Tools not available in Claude Code

**Solutions:**
1. Check `.mcp.json` path is correct
2. Verify `cwd` points to orchestrator directory
3. Restart Claude Code
4. Check server logs: `uv run python src/mcp/server.py` manually

### Python Agent Fails to Load

**Symptom:** `Agent class 'X' not found in module`

**Solutions:**
1. Check `AGENT.json` has `class_name` field
2. Verify agent path in `config/agents.json`
3. Ensure `agent.py` exists at agent path
4. Check Python syntax in `agent.py`

### Skill Not Found

**Symptom:** `Skill 'X' not found in config`

**Solutions:**
1. Verify skill listed in `config/skills.json`
2. Check `path` points to skill directory
3. Ensure `SKILL.md` exists in skill directory

### Interactive Menu Not Launching

**Symptom:** Menu crashes or doesn't display

**Solutions:**
1. Check `interactive_menu.py` exists in `src/orchestrator/`
2. Verify terminal supports interactive input
3. Run with `--list-skills` first to verify config loads

### Repository Not Found

**Symptom:** `Path does not exist` for repository

**Solutions:**
1. Verify repo path in `config/repos.json` is absolute
2. Check repository actually exists at that path
3. Ensure `active: true` in repo config
4. Use `--list-repos` to see configured repos

---

## Configuration Files

### `config/agents.json`

Defines all agents (Python and autonomous):

```json
{
  "agents": [
    {
      "name": "synth-notes-generator",
      "description": "Generate synthetic SOAP notes",
      "path": "/path/to/claude-toolkit/generated-agents/synth-notes-generator",
      "type": "python",
      "capabilities": ["prompt-loading", "api-calls", "file-operations"],
      "version": "1.0.0",
      "tags": ["healthcare", "data-generation"]
    }
  ]
}
```

### `config/skills.json`

Defines skills (template-driven):

```json
{
  "skills": [
    {
      "name": "repo-summarizer",
      "description": "Generate PROJECT.md for repositories",
      "path": "/path/to/claude-toolkit/generated-skills/repo-summarizer",
      "mode": "autonomous",
      "output": "PROJECT.md",
      "version": "1.0.0",
      "tags": ["documentation"]
    }
  ]
}
```

### `config/repos.json`

Defines repositories and groups:

```json
{
  "repositories": [
    {
      "name": "orchestrator",
      "path": "/Users/yourname/workspace/orchestrator",
      "active": true,
      "tags": ["active", "python"],
      "github": "yourorg/orchestrator"
    }
  ],
  "groups": {
    "active-projects": ["orchestrator", "claude-toolkit", "synthetic-notes"]
  }
}
```

---

## Next Steps

### For New Team Members

1. **Start with MCP Server** - Natural language, easiest to explore
2. **Try Interactive Menu** - Visual, helps discover capabilities
3. **Move to CLI** - For automation and scripting
4. **Learn tmux** - For advanced parallel workflows

### For Advanced Users

1. **Create custom Python agents** - See `claude-toolkit/generated-agents/`
2. **Build new MCP tools** - See `src/mcp/tools/` for patterns
3. **Design skills** - See `claude-toolkit/generated-skills/`
4. **Extend execution backends** - Docker, EC2 (future)

### Resources

- **Architecture Doc**: `docs/architecture/MCP_SERVER_ARCHITECTURE.md`
- **Agent Examples**: `claude-toolkit/generated-agents/*/agent.py`
- **Skill Templates**: `claude-toolkit/generated-skills/*/SKILL.md`
- **Config Examples**: `config/*.json`

---

## Summary

**Access Layers:**
1. **CLI** - `uv run python -m orchestrator --run-agent <agent> --task <task>`
2. **MCP** - "generate 10 SOAP notes" (from Claude Code)
3. **Menu** - `uv run python -m orchestrator --interactive`
4. **tmux** - Parallel windows/panes running any of the above

**Choose Based On:**
- **Automation/Scripts** → CLI
- **Natural Language** → MCP Server
- **Discovery/Batch** → Interactive Menu
- **Parallel/Long-running** → tmux

**All access the same core**, so use whichever fits your workflow.
