# Orchestrator Architecture

## Overview

The Generic Orchestrator is a multi-agent execution platform for running Claude skills and autonomous agents across multiple code repositories. It provides two execution modes: simple prompt-based execution and full agentic execution with tool use.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│  CLI Interface (orchestrator.py)                        │
│  - Argument parsing                                      │
│  - Skill selection                                       │
│  - Repository configuration                              │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Orchestrator Core (src/orchestrator/orchestrator.py)  │
│  - Skill loading & metadata extraction                  │
│  - Repository context collection                        │
│  - Execution mode routing                               │
│  - Results aggregation                                   │
└─────────────────────────────────────────────────────────┘
        ↓                                    ↓
┌──────────────────┐              ┌──────────────────────┐
│  Simple Mode     │              │  Agent Mode          │
│  - Single prompt │              │  - Multi-turn loop   │
│  - Text response │              │  - Tool execution    │
│  - File write    │              │  - Autonomous        │
└──────────────────┘              └──────────────────────┘
                                           ↓
                          ┌─────────────────────────────┐
                          │  Agent Runner               │
                          │  (agent_runner.py)          │
                          │  - Conversation management  │
                          │  - Tool use orchestration   │
                          │  - Iteration control        │
                          └─────────────────────────────┘
                                           ↓
                          ┌─────────────────────────────┐
                          │  Tool Executor              │
                          │  (agent_tools.py)           │
                          │  - read_file                │
                          │  - write_file               │
                          │  - list_files               │
                          │  - search_files             │
                          │  - run_bash                 │
                          └─────────────────────────────┘
```

## Components

### 1. CLI Interface (`orchestrator.py`)

The entry point that provides command-line interface for the orchestrator.

**Responsibilities:**
- Parse command-line arguments
- Load environment configuration
- Route to main orchestrator logic

**Key Arguments:**
- `--skill`: Skill name to execute
- `--repos`: Repository paths
- `--agent`: Enable agent mode (default)
- `--simple`: Use simple prompt mode
- `--output`: Custom output filename

### 2. Orchestrator Core (`src/orchestrator/orchestrator.py`)

The main orchestration logic that coordinates skill execution across repositories.

**Key Functions:**

- `load_skill(skill_name)`: Loads skill from toolkit
  - Reads SKILL.md
  - Extracts metadata (output location, filename patterns)
  - Loads optional templates

- `collect_repo_context(repo_path)`: Gathers repository information
  - File structure (up to 100 files)
  - README content
  - Package manifests

- `process_repo_with_skill(repo_path, skill, mode)`: Executes skill on repository
  - Routes to agent or simple mode
  - Handles output file management
  - Returns execution results

### 3. Agent Runner (`src/orchestrator/agent_runner.py`)

Implements the agentic execution loop with tool use capabilities.

**Key Features:**
- Multi-turn conversation with Claude
- Tool use orchestration
- Iteration limiting (max 25 by default)
- Execution tracking (files created, tool uses)

**Process:**
1. Build system prompt with skill definition
2. Collect initial repository context
3. Start conversation loop
4. Execute tools as requested by agent
5. Continue until agent signals completion or max iterations reached

### 4. Tool Executor (`src/orchestrator/agent_tools.py`)

Provides tool definitions and execution within repository context.

**Available Tools:**

1. **read_file**: Read file contents
   - Input: `{path: string}`
   - Output: `{content: string}`

2. **write_file**: Create/overwrite files
   - Input: `{path: string, content: string}`
   - Output: `{success: boolean, path: string}`

3. **list_files**: Glob pattern file listing
   - Input: `{pattern: string, path: string}`
   - Output: `{files: array, count: number, truncated: boolean}`

4. **search_files**: Text search with grep
   - Input: `{pattern: string, file_pattern?: string}`
   - Output: `{files: array, count: number}`

5. **run_bash**: Execute bash commands
   - Input: `{command: string}`
   - Output: `{stdout: string, stderr: string, returncode: number}`

**Safety Features:**
- All operations scoped to repository directory
- Timeout limits (30s for commands)
- Result truncation to prevent overwhelming output

## Execution Modes

### Simple Mode (Legacy)

Single prompt-response execution:
1. Build prompt with skill definition + repository context
2. Call Claude API once
3. Save text response to file
4. Done

**Use Cases:**
- Skills that generate single output file
- Backward compatibility
- Quick iterations during development

### Agent Mode (Default)

Multi-turn autonomous execution:
1. Agent receives skill definition and repository context
2. Agent uses tools to explore repository
3. Agent makes decisions about what to create
4. Agent creates multiple files as needed
5. Agent signals completion

**Use Cases:**
- Skills that create multiple files (e.g., MOC generator)
- Complex analysis requiring exploration
- Autonomous decision-making
- Full skill capability utilization

## Skill Loading

Skills are discovered from: `/Users/mpaz/workspace/claude-toolkit/generated-skills/`

Each skill must have:
- `SKILL.md`: Skill definition and instructions
- Optional `template.md`: Structure reference

**Metadata Extraction:**

The orchestrator automatically extracts:
- Output location (e.g., `docs/moc/`)
- Output filename patterns
- Directory creation requirements

Example:
```python
metadata = {
    "output_location": "docs/moc",
    "creates_directory": True,
    "output_filename": None
}
```

## Data Flow

### Agent Mode Execution Flow

```
User invokes CLI
  ↓
Load skill from toolkit
  ↓
Collect repository context
  ↓
Initialize AgentRunner
  ↓
Build system prompt with skill definition
  ↓
┌──────────── Agentic Loop ────────────┐
│                                       │
│  Send message to Claude               │
│    ↓                                  │
│  Receive response (text + tool uses)  │
│    ↓                                  │
│  Execute tools via ToolExecutor       │
│    ↓                                  │
│  Send tool results back to Claude     │
│    ↓                                  │
│  Repeat until agent signals done      │
│                                       │
└───────────────────────────────────────┘
  ↓
Collect execution summary
  ↓
Return results (files created, iterations, etc.)
```

## Configuration

### Environment Variables

`.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

### Default Repositories

Configured in `orchestrator.py`:
```python
DEFAULT_REPOS = [
    "/Users/mpaz/workspace/mcp-fleet",
    "/Users/mpaz/workspace/rishi",
]
```

### Skills Base Path

```python
SKILLS_BASE_PATH = "/Users/mpaz/workspace/claude-toolkit/generated-skills"
```

## Extension Points

### Adding New Tools

1. Add tool definition to `get_tool_definitions()` in `agent_tools.py`
2. Implement executor method in `ToolExecutor` class
3. Tools are automatically available to all agents

### Adding Skills

1. Create new directory in skills toolkit
2. Add `SKILL.md` with skill definition
3. Optional: Add `template.md`
4. Skill automatically discovered by orchestrator

### Custom Execution Modes

Add new execution mode in `process_repo_with_skill()`:
```python
elif use_custom_mode:
    # Custom execution logic
    pass
```

## Future Architecture Considerations

### Session Management

For tmux integration and multi-session support:
- Session state persistence
- Resume/pause/kill capabilities
- Session status monitoring

### GitHub Integration

For issue-driven development:
- Issue fetching and parsing
- Context injection from issues
- Result posting back to GitHub

### Human-in-the-Loop

For intervention points:
- Checkpoint system
- Approval gates for destructive operations
- Interactive prompts during execution

### Parallel Execution

For batch processing:
- Process pool for concurrent agents
- Resource management
- Progress aggregation
