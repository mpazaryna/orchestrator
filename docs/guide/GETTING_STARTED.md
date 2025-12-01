# Getting Started

Quick guide to setting up and running the orchestrator.

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management
- Anthropic API key

## Installation

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

Edit `.env` and replace `your-api-key-here` with your actual Anthropic API key:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
```

Get your API key from: https://console.anthropic.com/settings/keys

### 3. Configure Your Repositories

Edit `repos.json` to add your repositories:

```json
{
  "repositories": [
    {
      "name": "my-app",
      "path": "/Users/you/projects/my-app",
      "github": "https://github.com/you/my-app",
      "description": "My awesome application",
      "tags": ["web", "python"],
      "active": true
    }
  ],
  "groups": {
    "all": ["my-app"],
    "production": ["my-app"]
  }
}
```

See [Repository Configuration](REPOSITORY_CONFIG.md) for detailed setup.

## Verify Installation

List configured repositories:

```bash
uv run python orchestrator.py --list-repos
```

List available skills:

```bash
uv run python orchestrator.py --list-skills
```

## Next Steps

- Learn about [Usage Modes](USAGE_MODES.md)
- Explore [Example Workflows](EXAMPLES.md)
- Review [CLI Reference](CLI_REFERENCE.md)
