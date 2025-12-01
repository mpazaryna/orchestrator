# Generic Orchestrator for Claude Skills

A flexible Python orchestrator that runs **any skill** from your Claude toolkit against multiple local repositories using the Claude API.

## Features

- **Skill-Agnostic**: Run any skill from your toolkit (repo-summarizer, code-reviewer, etc.)
- **Parallel Execution**: Process multiple repositories simultaneously for fast completion
- **Three Operational Modes**: Interactive (with Claude Code), CLI (direct), and Autonomous (unattended)
- **Task Configuration**: JSON-based task definitions for overnight runs and cron jobs
- **Flexible Repository Selection**: By name, group, tag, or path
- **Smart Defaults**: Sensible defaults with easy overrides

## Quick Start

```bash
# Install dependencies
uv sync

# Set up your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Configure repositories in repos.json
# See docs/guide/REPOSITORY_CONFIG.md

# Run on all active repos
uv run python orchestrator.py

# Run specific skill
uv run python orchestrator.py --skill code-reviewer --group production
```

## Documentation

### Getting Started
- [Installation & Setup](docs/guide/GETTING_STARTED.md) - Install dependencies, configure API key and repositories
- [Repository Configuration](docs/guide/REPOSITORY_CONFIG.md) - Configure repos.json with groups and tags

### Usage
- [Usage Modes](docs/guide/USAGE_MODES.md) - Interactive, CLI, and Autonomous modes
- [CLI Reference](docs/guide/CLI_REFERENCE.md) - Complete command-line options
- [Example Workflows](docs/guide/EXAMPLES.md) - Common use cases and patterns
- [Autonomous Mode](docs/AUTONOMOUS_MODE.md) - Overnight runs, cron jobs, CI/CD integration

## Three Operational Modes

### 1. Interactive Mode (with Claude Code)
```bash
cd ~/workspace/orchestrator
claude
> "Run repo-summarizer across all my repos"
```

### 2. CLI Mode (Direct Execution)
```bash
# Fast parallel processing
uv run python orchestrator.py --skill repo-summarizer --group all

# Sequential processing
uv run python orchestrator.py --sequential --repos /path/to/repo
```

### 3. Autonomous Mode (Unattended)
```bash
# Overnight runs with task configuration
nohup uv run python orchestrator.py --config config/overnight.json &

# Monitor progress
tail -f ~/.orchestrator/logs/overnight.log
```

## Project Structure

```
orchestrator/
├── src/orchestrator/          # Main package
│   ├── orchestrator.py       # Main orchestrator logic
│   ├── agent_runner.py       # Agentic execution loop
│   ├── agent_tools.py        # Tool definitions & execution
│   ├── python_agent_runner.py # Python agent support
│   └── config.py             # Configuration loader
├── docs/
│   ├── guide/                # User guides
│   │   ├── GETTING_STARTED.md
│   │   ├── USAGE_MODES.md
│   │   ├── REPOSITORY_CONFIG.md
│   │   ├── CLI_REFERENCE.md
│   │   └── EXAMPLES.md
│   ├── AUTONOMOUS_MODE.md    # Autonomous execution guide
│   └── reference/            # Technical references
├── config/                    # Task configurations
│   ├── tasks.example.json
│   └── overnight.json
├── tests/                     # Test suite
├── orchestrator.py           # Convenience entry point
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/orchestrator
```

### Installing for Development

```bash
# Install in editable mode
uv pip install -e .
```

## License

MIT License - See LICENSE.txt for details