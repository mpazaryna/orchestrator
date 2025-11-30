# Quick Start Guide

## First Time Setup

1. **Install dependencies**:
```bash
uv sync
```

2. **Configure API key**:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

3. **Configure repositories** (edit `repos.json`):
```json
{
  "repositories": [
    {
      "name": "my-project",
      "path": "/path/to/my-project",
      "github": "https://github.com/user/project",
      "tags": ["web", "python"],
      "active": true
    }
  ],
  "groups": {
    "all": ["my-project"]
  }
}
```

## Common Commands

### Discovery
```bash
# See all configured repos
uv run python orchestrator.py --list-repos

# See repo groups
uv run python orchestrator.py --list-groups

# See available skills
uv run python orchestrator.py --list-skills
```

### Run Skills

```bash
# Run on all active repos
uv run python orchestrator.py --skill repo-summarizer

# Run on specific group
uv run python orchestrator.py --skill code-reviewer --group production

# Run on specific repos by name
uv run python orchestrator.py --skill repo-summarizer --repo-names mcp-fleet rishi

# Run on repos with tag
uv run python orchestrator.py --skill code-reviewer --tag python

# Use simple mode (faster, single-file output)
uv run python orchestrator.py --skill repo-summarizer --simple
```

### tmux Workflow (Recommended for Multiple Repos)

```bash
# Start tmux session
./tmux_experiment.sh

# Inside tmux:
# - Window 0: Dashboard (instructions)
# - Window 1: Run orchestrator
# - Window 2: Monitor results
# - Window 3: Shell for other commands

# Switch windows: Ctrl+b [0-3]
# Detach: Ctrl+b d
# Reattach: tmux attach -t orchestrator-demo
```

## Execution Modes

### Agent Mode (Default)
- Multi-turn autonomous execution
- Can create multiple files
- Uses tools (read, write, search, bash)
- Best for complex skills like `project-moc-generator`

```bash
uv run python orchestrator.py --skill project-moc-generator --repo-names my-project
```

### Simple Mode
- Single prompt-response
- Creates one output file
- Faster execution
- Best for single-document skills like `repo-summarizer`

```bash
uv run python orchestrator.py --skill repo-summarizer --simple
```

## Example Workflows

### Document All Projects
```bash
# Generate PROJECT.md for all production repos
uv run python orchestrator.py --skill repo-summarizer --group production
```

### Code Review Sprint
```bash
# Review all Python projects
uv run python orchestrator.py --skill code-reviewer --tag python
```

### Create Documentation
```bash
# Generate MOC documentation for specific project
uv run python orchestrator.py --skill project-moc-generator --repo-names my-app
```

### Multi-Repo Analysis
```bash
# Start tmux session for parallel monitoring
./tmux_experiment.sh code-reviewer all

# In orchestrator window (tmux window 1):
uv run python orchestrator.py --skill code-reviewer --group all

# Switch to monitor window (Ctrl+b 2) to see progress
```

## Configuration Tips

### Repository Tags
Use tags to organize repos by:
- Technology: `python`, `typescript`, `rust`
- Type: `web`, `cli`, `library`, `api`
- Status: `production`, `experimental`, `archived`
- Domain: `ai`, `crypto`, `web3`

### Groups
Create groups for common workflows:
- `production`: Live projects
- `personal`: Side projects
- `client-work`: Client repos
- `learning`: Educational projects

Example `repos.json`:
```json
{
  "repositories": [
    {"name": "api", "path": "/code/api", "tags": ["python", "production", "api"]},
    {"name": "web", "path": "/code/web", "tags": ["typescript", "production", "web"]},
    {"name": "cli", "path": "/code/cli", "tags": ["rust", "personal", "cli"]}
  ],
  "groups": {
    "all": ["api", "web", "cli"],
    "production": ["api", "web"],
    "personal": ["cli"],
    "python-projects": ["api"],
    "typescript-projects": ["web"]
  }
}
```

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Check `.env` file exists and has your API key
- Don't commit `.env` to git (use `.env.example` as template)

### "Skill not found"
- Run `--list-skills` to see available skills
- Skills must be in: `/Users/mpaz/workspace/claude-toolkit/generated-skills/`

### "Repository path does not exist"
- Check paths in `repos.json` are correct
- Use absolute paths, not relative

### Agent takes too long
- Use `--simple` mode for faster execution
- Check agent isn't stuck in a loop (max 25 iterations)

## Next Steps

1. Add your repositories to `repos.json`
2. Try the tmux experiment: `./tmux_experiment.sh`
3. Read `TMUX_EXPERIMENT.md` for advanced tmux usage
4. Read `ARCHITECTURE.md` to understand the system
5. Write tests in `tests/` directory
