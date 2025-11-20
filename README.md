# Generic Orchestrator for Claude Skills

A flexible Python orchestrator that runs **any skill** from your Claude toolkit against multiple local repositories using the Claude API.

## Features

- **Skill-Agnostic**: Run any skill from your toolkit (repo-summarizer, code-reviewer, etc.)
- **Batch Processing**: Analyze multiple repositories in a single run
- **Flexible Configuration**: CLI arguments for skill selection, custom repos, and output files
- **Smart Defaults**: Sensible defaults with easy overrides
- **Uses Claude API (Sonnet 4)**: Intelligent code analysis and generation
- **Comprehensive Context**: Collects repository structure, README, package files
- **Tracking**: Saves results to JSON for auditing and monitoring

## Setup

### 1. Install Dependencies

This project uses `uv` for dependency management:

```bash
uv sync
```

### 2. Set Your Anthropic API Key

Copy the example environment file and add your API key:

```bash
cp .env.example .env
```

Then edit `.env` and replace `your-api-key-here` with your actual Anthropic API key:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
```

Get your API key from: https://console.anthropic.com/settings/keys

### 3. (Optional) Configure Default Repository Paths

Edit `orchestrator.py` and update the `DEFAULT_REPOS` list with your commonly-used repository paths:

```python
DEFAULT_REPOS = [
    "/Users/mpaz/workspace/mcp-fleet",
    "/Users/mpaz/workspace/rishi",
    # Add more repo paths here
]
```

Or pass repositories via the `--repos` flag (see Usage below).

## Usage

### List Available Skills

See all skills in your toolkit:

```bash
uv run python orchestrator.py --list-skills
```

### Run with Default Skill (repo-summarizer)

```bash
# Run on default repositories
uv run python orchestrator.py

# Run on specific repositories
uv run python orchestrator.py --repos /path/to/repo1 /path/to/repo2
```

### Run a Different Skill

```bash
# Run code-reviewer on a repository
uv run python orchestrator.py --skill code-reviewer --repos /path/to/repo

# Run project-moc-generator
uv run python orchestrator.py --skill project-moc-generator --repos /path/to/repo

# Custom output filename
uv run python orchestrator.py --skill code-reviewer --repos /path/to/repo --output review.md
```

### Command-Line Options

```
--skill, -s        Skill name to run (default: repo-summarizer)
--repos, -r        Repository paths (space-separated)
--output, -o       Custom output filename
--list-skills      List all available skills
```

## How It Works

For each repository, the orchestrator:

1. **Loads the Skill**:
   - Reads SKILL.md from your toolkit
   - Loads optional template files if available
   - Prepares skill-specific instructions

2. **Collects Context**:
   - Repository file structure (up to 100 files)
   - README.md content
   - Package manifests (package.json, pyproject.toml, requirements.txt, etc.)

3. **Executes with Claude**:
   - Uses Claude Sonnet 4 to run the skill
   - Passes repository context and skill definition
   - Generates output according to skill specifications

4. **Saves Results**:
   - Writes output to each repository (e.g., PROJECT.md, code-review.md)
   - Saves summary to ~/orchestrator_{skill-name}_results.json

## Available Skills

Your toolkit includes 12+ skills:

- **repo-summarizer**: Generate professional PROJECT.md portfolio documentation
- **code-reviewer**: Review code for best practices and potential issues
- **project-moc-generator**: Create Map of Content for projects
- **commit-helper**: Assist with commit message generation
- **technical-decision**: Document technical decisions
- **spike-driven-dev**: Guide spike-driven development
- And more! Use `--list-skills` to see all

## Example Workflows

### Portfolio Generation

```bash
# Generate PROJECT.md for all your projects
uv run python orchestrator.py --skill repo-summarizer --repos \
  ~/projects/app1 ~/projects/app2 ~/projects/lib1
```

### Code Review Batch

```bash
# Review multiple repositories
uv run python orchestrator.py --skill code-reviewer --repos \
  ~/work/service-a ~/work/service-b --output code-review.md
```

### Documentation Sprint

```bash
# Generate technical decisions for microservices
uv run python orchestrator.py --skill technical-decision --repos \
  ~/microservices/*
```

## Project Structure

```
orchestrator/
├── src/orchestrator/          # Main package
│   ├── __init__.py           # Package initialization
│   ├── __main__.py           # CLI entry point
│   ├── orchestrator.py       # Main orchestrator logic
│   ├── agent_runner.py       # Agentic execution loop
│   └── agent_tools.py        # Tool definitions & execution
├── tests/                     # Test suite
│   ├── test_orchestrator.py
│   ├── test_agent_runner.py
│   └── test_agent_tools.py
├── orchestrator.py            # Convenience entry point
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

# Run specific test file
uv run pytest tests/test_agent_tools.py -v
```

### Installing for Development

```bash
# Install in editable mode
uv pip install -e .
```

## Future Enhancements

- Parallel processing for faster batch operations
- tmux session management for long-running tasks
- Integration with GitHub project manager JSON
- Custom templates per repository type
- Web UI dashboard for results visualization
- Incremental updates (only re-analyze changed repos)
- Human-in-the-loop intervention points
- Session persistence and resumability