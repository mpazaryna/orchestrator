# Usage Modes

The orchestrator operates in three distinct modes to support different workflows.

## 1. Interactive Mode (via Claude Code)

When working in Claude Code, the orchestrator acts as a subagent for batch processing.

**Use case:** Interactive development with Claude Code as your main agent

```bash
cd ~/workspace/orchestrator
claude

> "Run repo-summarizer across all my repos"
```

Claude Code will invoke the orchestrator as a subagent, process your repositories, and report back with results.

## 2. CLI Mode (Direct Execution)

Run the orchestrator directly from the command line for on-demand batch processing.

**Use case:** Quick ad-hoc repository analysis and documentation generation

### Fast Parallel Processing

```bash
# Process all repos in parallel (default behavior)
uv run python orchestrator.py --skill repo-summarizer --group all

# All 5 repos processed simultaneously - completes in ~1-2 minutes
```

### Control Parallelism

```bash
# Sequential processing (if needed)
uv run python orchestrator.py --skill repo-summarizer --group all --sequential

# Customize max parallel workers (default: 5)
uv run python orchestrator.py --skill repo-summarizer --group all --max-workers 10
```

### Repository Selection

```bash
# Run on all active repositories from config
uv run python orchestrator.py

# Run on specific repository group
uv run python orchestrator.py --group production

# Run on repositories by name
uv run python orchestrator.py --repo-names mcp-fleet rishi

# Run on repositories with specific tag
uv run python orchestrator.py --tag ai

# Run on specific paths (bypasses config)
uv run python orchestrator.py --repos /path/to/repo1 /path/to/repo2
```

### Run Different Skills

```bash
# Run code-reviewer on a repository
uv run python orchestrator.py --skill code-reviewer --repos /path/to/repo

# Run project-moc-generator
uv run python orchestrator.py --skill project-moc-generator --repos /path/to/repo

# Custom output filename
uv run python orchestrator.py --skill code-reviewer --repos /path/to/repo --output review.md
```

## 3. Autonomous Mode (Unattended Execution)

Run the orchestrator unattended for overnight processing, cron jobs, or distributed execution.

**Use case:** Scheduled documentation updates, CI/CD integration, distributed processing

### Quick Start

```bash
# Run task configuration in background
nohup uv run python orchestrator.py --config config/overnight.json &

# Check progress
tail -f ~/.orchestrator/logs/overnight.log
```

### Task Configuration

Create a JSON file defining tasks to run:

```json
{
  "description": "Overnight documentation update",
  "tasks": [
    {"name": "Update READMEs", "skill": "readme-generator", "group": "all", "enabled": true},
    {"name": "Update PROJECT.md", "skill": "repo-summarizer", "group": "all", "enabled": true}
  ],
  "settings": {
    "parallel": true,
    "max_workers": 5,
    "simple_mode": true,
    "log_file": "~/.orchestrator/logs/overnight.log"
  }
}
```

### Common Patterns

**Cron Job (Daily Updates):**

```cron
# Update docs every night at 2 AM
0 2 * * * cd /Users/mpaz/workspace/orchestrator && uv run python orchestrator.py --config config/overnight.json
```

**CI/CD Integration:**

See [Autonomous Mode Guide](../AUTONOMOUS_MODE.md) for GitHub Actions examples.

**Distributed Execution:**

Run different repos on different machines:

```bash
# Server 1
uv run python orchestrator.py --skill repo-summarizer --repo-names mcp-fleet rishi

# Server 2
uv run python orchestrator.py --skill repo-summarizer --repo-names orchestrator synthetic-notes
```

## Simple Mode vs Agent Mode

### Simple Mode (Recommended for autonomous runs)

- Single API call per repo
- Fast (~30-60 seconds per repo)
- Deterministic output
- Lower cost

```bash
uv run python orchestrator.py --simple
```

### Agent Mode

- Multiple iterations with tool use
- Slower (~2-5 minutes per repo)
- More thorough analysis
- Higher cost

```bash
# Agent mode is default, or explicitly enable
uv run python orchestrator.py
```

## Next Steps

- See [CLI Reference](CLI_REFERENCE.md) for all command-line options
- Explore [Example Workflows](EXAMPLES.md)
- Read the complete [Autonomous Mode Guide](../AUTONOMOUS_MODE.md)
