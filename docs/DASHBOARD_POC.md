# Orchestrator Dashboard - Proof of Concept

Visual command center for managing your agent army using [Textual](https://textual.textualize.io/).

---

## Overview

The dashboard provides a rich TUI (Text User Interface) for:
- **Viewing agents** - All configured agents with status cards
- **Monitoring jobs** - Real-time progress of running agents
- **Viewing logs** - Live output from agent execution
- **Managing config** - View agents, skills, repositories

---

## Launch

```bash
uv run orchestrator --dashboard
```

### ⚠️ Important: Terminal Requirements

The dashboard requires a **native interactive terminal** to function properly.

**❌ Won't work in:**
- VS Code integrated terminals (including Claude Code)
- Piped commands or redirected output
- Non-TTY environments
- IDEs with limited ANSI escape code support

**✅ Works in:**
- macOS Terminal.app
- iTerm2
- GNOME Terminal, Konsole (Linux)
- Windows Terminal
- Any native terminal application with full ANSI support

**Why?** Textual uses advanced ANSI escape codes for rendering. VS Code's integrated terminal doesn't fully support these codes, resulting in raw escape sequences being displayed instead of the rendered UI.

**Solution:** Open a native terminal and run the command there.

**Keyboard shortcuts:**
- `q` - Quit
- `d` - Toggle dark mode
- `r` - Refresh data
- `Tab` - Navigate between tabs
- `Space` - Activate buttons

---

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Orchestrator                                    [Dark Mode] │
├─────────────────────────────────────────────────────────────┤
│ [Overview] [Agents] [Jobs] [Logs] [Config]                 │
├──────────────┬──────────────────────────────────────────────┤
│ Available    │ Running Jobs                                 │
│ Agents       │                                              │
│              │ ┌────────────────────────────────────────┐   │
│ ┌──────────┐ │ │ github-pm-analyzer: daily_activity     │   │
│ │synth-notes│ │ │ ████████████████░░░░ 80%               │   │
│ │          │ │ │ Processing... 80% complete              │   │
│ │Generate  │ │ └────────────────────────────────────────┘   │
│ │synthetic │ │                                              │
│ │SOAP notes│ │                                              │
│ │          │ │                                              │
│ │Type: py  │ │                                              │
│ │Status:   │ │                                              │
│ │idle      │ │                                              │
│ └──────────┘ │                                              │
│              │                                              │
│ ┌──────────┐ │                                              │
│ │github-pm │ │                                              │
│ │analyzer  │ │                                              │
│ │...       │ │                                              │
│ └──────────┘ │                                              │
└──────────────┴──────────────────────────────────────────────┘
[Run Agent] [Run Skill] [Stop All] [Refresh]
 q Quit | d Dark | r Refresh
```

---

## Tabs

### 1. Overview
**Split panel view:**
- **Left**: Agent cards showing all configured agents
- **Right**: Running jobs with live progress bars

**Demo**: Click "Run Agent" to see a simulated job

### 2. Agents
**Data table** showing all agents:
- Name
- Type (python, autonomous)
- Version
- Capabilities
- Tags

### 3. Jobs
**Jobs table** tracking execution history:
- Job ID
- Agent name
- Status (running, completed, failed)
- Progress
- Start time

### 4. Logs
**Live log viewer** with auto-scroll:
```
[12:34:15] Dashboard initialized
[12:34:20] Starting demo agent: github-pm-analyzer
[12:34:25] github-pm-analyzer: 10% complete
[12:34:30] github-pm-analyzer: 20% complete
...
[12:35:10] ✅ github-pm-analyzer completed successfully
```

### 5. Config
**Configuration summary:**
- Total agents
- Total skills
- Total repositories
- Agent type breakdown

---

## Features Implemented (POC)

✅ **Agent Discovery**
- Loads from `config/agents.json`
- Displays all agents with metadata
- Visual cards with type, status

✅ **Demo Job Execution**
- Click "Run Agent" to see simulated job
- Progress bar updates in real-time
- Live log messages
- Job added to history table

✅ **Multi-tab Interface**
- Overview, Agents, Jobs, Logs, Config
- Tab navigation with keyboard
- Clean separation of concerns

✅ **Live Logs**
- Auto-scrolling log viewer
- Timestamped messages
- Color-coded output

✅ **Dark Mode Toggle**
- Press `d` to switch
- Persists across tabs

✅ **Refresh**
- Re-loads agent config
- Updates all displays
- Press `r` or click button

---

## Next Steps (Future Enhancement)

### Phase 1: Real Agent Execution
- [ ] Actually run Python agents from dashboard
- [ ] Connect to `PythonAgentRunner`
- [ ] Stream real output to logs
- [ ] Handle errors and failures

### Phase 2: Interactive Controls
- [ ] Select agents from list to run
- [ ] Configure task parameters in modal
- [ ] Multi-select for batch operations
- [ ] Cancel/pause running jobs

### Phase 3: Job Queue
- [ ] Queue multiple jobs
- [ ] Priority scheduling
- [ ] Parallel execution limits
- [ ] Job dependencies

### Phase 4: Advanced Monitoring
- [ ] Cost tracking (API usage)
- [ ] Time estimates
- [ ] Resource usage (CPU, memory)
- [ ] Historical metrics

### Phase 5: Remote Backends
- [ ] View Docker container jobs
- [ ] Monitor EC2 instance jobs
- [ ] Remote log streaming
- [ ] Distributed status

### Phase 6: Workflow Builder
- [ ] Visual workflow designer
- [ ] Drag-drop agents
- [ ] Configure dependencies
- [ ] Save/load workflows

---

## Technical Details

### Built With
- **Textual 0.43+** - Rich TUI framework
- **Reactive widgets** - Auto-updating UI
- **Async workers** - Non-blocking job execution
- **CSS styling** - Custom theme

### Architecture

```
dashboard.py
├── OrchestratorDashboard (App)
│   ├── Header/Footer
│   ├── TabbedContent
│   │   ├── Overview (Horizontal split)
│   │   │   ├── Agents panel (VerticalScroll)
│   │   │   │   └── AgentCard widgets
│   │   │   └── Jobs panel (VerticalScroll)
│   │   │       └── JobStatus widgets
│   │   ├── Agents (DataTable)
│   │   ├── Jobs (DataTable)
│   │   ├── Logs (Log widget)
│   │   └── Config (Static)
│   └── Action buttons (Horizontal)
├── AgentCard (Custom widget)
│   ├── Agent name
│   ├── Description
│   ├── Metadata
│   └── Progress bar
└── JobStatus (Custom widget)
    ├── Job name
    ├── Progress bar (reactive)
    └── Status message (reactive)
```

### Key Components

**1. AgentCard**
- Displays individual agent
- Shows type, description, status
- Progress bar for active jobs

**2. JobStatus**
- Tracks running job
- Reactive progress updates
- Status messages

**3. Reactive Properties**
```python
class JobStatus(Static):
    progress: reactive[int] = reactive(0)

    def watch_progress(self, progress: int):
        # Auto-updates UI when progress changes
        bar.update(progress=progress)
```

**4. Async Workers**
```python
@work(exclusive=True)
async def run_demo_agent(self):
    # Non-blocking execution
    # Updates UI during execution
```

---

## Code Integration

### Entry Point

Added to `orchestrator.py`:
```python
parser.add_argument(
    "--dashboard",
    action="store_true",
    help="Launch Textual TUI dashboard"
)

if args.dashboard:
    from .dashboard import run_dashboard
    run_dashboard()
    return 0
```

### Config Loading

Uses existing `ConfigLoader`:
```python
from .config import ConfigLoader

config_loader = ConfigLoader()
agents = config_loader.list_agents()
```

### Future: Real Execution

Will integrate with:
```python
from .python_agent_runner import PythonAgentRunner

runner = PythonAgentRunner(client)
result = runner.run_agent(agent_config, task_config)
```

---

## Comparison to Other Access Layers

| Feature | CLI | MCP | Menu | **Dashboard** |
|---------|-----|-----|------|---------------|
| Visual | ❌ | ❌ | ⚠️ | ✅ Rich UI |
| Real-time | ❌ | ❌ | ❌ | ✅ Live updates |
| Monitoring | ❌ | ❌ | ❌ | ✅ Progress bars |
| Logs | ❌ | ❌ | ❌ | ✅ Live viewer |
| Batch ops | ✅ | ❌ | ✅ | ✅ (future) |
| Remote | ❌ | ✅ | ❌ | ✅ (future) |

**Dashboard fills the gap:** Visual monitoring and control for local/remote agent execution.

---

## Demo Usage

**1. Launch:**
```bash
cd /path/to/orchestrator
uv run python -m orchestrator --dashboard
```

**2. Navigate:**
- Use `Tab` to switch between Overview, Agents, Jobs, Logs, Config
- Press `r` to refresh data
- Press `d` to toggle dark mode

**3. Run Demo:**
- Click "Run Agent" button
- Watch progress bar in "Running Jobs" panel
- See log messages appear in real-time
- Job completes and appears in Jobs table

**4. Explore:**
- Click "Agents" tab to see all agents in table
- Click "Logs" tab to see full log history
- Click "Config" tab to see configuration

**5. Quit:**
- Press `q` to exit

---

## Screenshots (Text)

**Overview Tab:**
```
╭─ Available Agents ────────╮╭─ Running Jobs ──────────────╮
│                           ││                             │
│ ┏━━━━━━━━━━━━━━━━━━━━━━┓ ││ ┏━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃ synth-notes-generator┃ ││ ┃ github-pm-analyzer    ┃ │
│ ┃ Generate synthetic   ┃ ││ ┃ ████████████░░░░ 80%  ┃ │
│ ┃ SOAP notes          ┃ ││ ┃ Processing repos...   ┃ │
│ ┃ Type: python        ┃ ││ ┗━━━━━━━━━━━━━━━━━━━━━━━┛ │
│ ┃ Status: idle        ┃ ││                             │
│ ┗━━━━━━━━━━━━━━━━━━━━━━┛ ││                             │
╰───────────────────────────╯╰─────────────────────────────╯
```

**Logs Tab:**
```
╭─ Output Log ───────────────────────────────────────────╮
│ [12:34:15] Dashboard initialized                      │
│ [12:34:20] Starting demo agent: github-pm-analyzer    │
│ [12:34:25] github-pm-analyzer: 10% complete           │
│ [12:34:30] github-pm-analyzer: 20% complete           │
│ [12:34:35] github-pm-analyzer: 30% complete           │
│ ...                                                    │
│ [12:35:10] ✅ github-pm-analyzer completed successfully│
╰────────────────────────────────────────────────────────╯
```

---

## Why This Matters

**For your "Agent Army" vision:**

1. **Visibility** - See all agents, their status, what's running
2. **Control** - Start, stop, queue jobs from one place
3. **Monitoring** - Real-time progress, costs, logs
4. **Scalability** - Foundation for remote backend monitoring
5. **Discoverability** - See what agents you have, what they do

**Next evolution:**
- Add real execution (not just demo)
- Connect to Docker/EC2 backends
- Build workflow designer
- Add job scheduling

This POC proves the dashboard concept works and integrates cleanly with the orchestrator.

---

## Resources

- [Textual Documentation](https://textual.textualize.io/)
- [Widget Gallery](https://textual.textualize.io/widget_gallery/)
- [Textual Examples](https://github.com/Textualize/textual/tree/main/examples)

---

## Summary

✅ **POC Complete** - Dashboard launches, displays agents, runs demo jobs, shows logs
✅ **Integrated** - Works with existing config/agents
✅ **Extensible** - Clean architecture for adding real execution
✅ **Usable** - Keyboard nav, dark mode, multi-tabs

**Next**: Wire up real agent execution and you have a visual command center for your agent army.
