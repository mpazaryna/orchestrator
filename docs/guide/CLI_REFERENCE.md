# CLI Reference

Complete reference for orchestrator command-line options.

## Basic Usage

```bash
uv run python orchestrator.py [OPTIONS]
```

## Execution Modes

### `--simple`

Run in simple prompt mode (fast, single API call per repo)

```bash
uv run python orchestrator.py --simple
```

- Single API call per repository
- Faster execution (~30-60 seconds per repo)
- Deterministic output
- Lower cost
- Recommended for autonomous runs

### `--parallel` / `--sequential`

Control parallel execution (default: parallel)

```bash
# Parallel processing (default)
uv run python orchestrator.py --parallel

# Sequential processing
uv run python orchestrator.py --sequential
```

### `--max-workers N`

Maximum number of parallel workers (default: 5)

```bash
uv run python orchestrator.py --max-workers 10
```

## Repository Selection

### `--skill, -s SKILL`

Skill name to run (default: repo-summarizer)

```bash
uv run python orchestrator.py --skill code-reviewer
```

### `--repos, -r PATH [PATH ...]`

Repository paths (space-separated, bypasses config)

```bash
uv run python orchestrator.py --repos /path/to/repo1 /path/to/repo2
```

### `--repo-names NAME [NAME ...]`

Repository names from config

```bash
uv run python orchestrator.py --repo-names mcp-fleet orchestrator
```

### `--group, -g GROUP`

Process repository group from config

```bash
uv run python orchestrator.py --group production
```

### `--tag, -t TAG`

Process repositories by tag

```bash
uv run python orchestrator.py --tag python
```

## Output Options

### `--output, -o FILENAME`

Custom output filename

```bash
uv run python orchestrator.py --output custom-review.md
```

### `--log-file PATH`

Log file path for autonomous execution (default: stdout)

```bash
uv run python orchestrator.py --log-file logs/run.log
```

## Autonomous Mode

### `--config, -c PATH`

Task configuration file (JSON) for autonomous execution

```bash
uv run python orchestrator.py --config config/overnight.json
```

See [Autonomous Mode Guide](../AUTONOMOUS_MODE.md) for task configuration format.

## Information Commands

### `--list-skills`

List all available skills from claude-toolkit

```bash
uv run python orchestrator.py --list-skills
```

### `--list-repos`

List configured repositories from repos.json

```bash
uv run python orchestrator.py --list-repos
```

### `--list-groups`

List repository groups from repos.json

```bash
uv run python orchestrator.py --list-groups
```

### `--list-agents`

List available agents

```bash
uv run python orchestrator.py --list-agents
```

### `--interactive, -i`

Interactive menu mode

```bash
uv run python orchestrator.py --interactive
```

## Agent-Specific Options

### Python Agent

For running Python-based agents:

```bash
uv run python orchestrator.py --run-agent python-mcp-writer --repos /path/to/repo
```

### GitHub PM Analyzer

```bash
# Analyze recent issues
uv run python orchestrator.py --run-agent github-pm-analyzer

# Specify days to analyze
uv run python orchestrator.py --run-agent github-pm-analyzer --days 14
```

## Examples

### Quick Repository Summary

```bash
uv run python orchestrator.py
```

### Code Review with Custom Output

```bash
uv run python orchestrator.py \
  --skill code-reviewer \
  --repos ~/projects/my-app \
  --output my-app-review.md
```

### Parallel Processing with Multiple Workers

```bash
uv run python orchestrator.py \
  --skill repo-summarizer \
  --group all \
  --max-workers 10
```

### Simple Mode for Fast Execution

```bash
uv run python orchestrator.py \
  --simple \
  --skill readme-generator \
  --tag production
```

### Autonomous Overnight Run

```bash
nohup uv run python orchestrator.py \
  --config config/overnight.json \
  --log-file ~/.orchestrator/logs/overnight.log &
```

## Exit Codes

- `0`: Success
- `1`: Error (invalid config, missing files, etc.)

## Environment Variables

### `ANTHROPIC_API_KEY`

Required. Your Anthropic API key.

Set in `.env` file:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
```

Or export in shell:

```bash
export ANTHROPIC_API_KEY=sk-ant-api03-...
```

## Next Steps

- See [Usage Modes](USAGE_MODES.md) for common patterns
- Explore [Example Workflows](EXAMPLES.md)
- Read [Getting Started](GETTING_STARTED.md) for setup
