# Example Workflows

Common workflows and use cases for the orchestrator.

## Portfolio Generation

Generate professional PROJECT.md files for all your projects.

```bash
# Generate PROJECT.md for all active repositories
uv run python orchestrator.py --skill repo-summarizer

# Generate for specific projects
uv run python orchestrator.py --skill repo-summarizer --repos \
  ~/projects/app1 ~/projects/app2 ~/projects/lib1

# Generate for production repos only
uv run python orchestrator.py --skill repo-summarizer --group production
```

**Output:** Creates `PROJECT.md` in each repository with:
- Project overview and purpose
- Key features and capabilities
- Technical stack and architecture
- Setup and usage instructions

## Code Review Batch

Review multiple repositories for best practices and potential issues.

```bash
# Review all repositories
uv run python orchestrator.py --skill code-reviewer --group all

# Review specific services
uv run python orchestrator.py --skill code-reviewer --repos \
  ~/work/service-a ~/work/service-b --output code-review.md

# Review with simple mode (faster)
uv run python orchestrator.py --simple --skill code-reviewer --tag python
```

**Output:** Creates code review reports highlighting:
- Code quality issues
- Best practice violations
- Potential bugs or security concerns
- Improvement suggestions

## Documentation Sprint

Generate or update documentation across multiple projects.

```bash
# Update READMEs for all repos
uv run python orchestrator.py --skill readme-generator --group all

# Generate technical decision docs for microservices
uv run python orchestrator.py --skill technical-decision --repos ~/microservices/*

# Create Maps of Content for all projects
uv run python orchestrator.py --skill project-moc-generator --group all
```

## Overnight Documentation Update

Set up automated overnight documentation updates.

**1. Create task configuration** (`config/nightly-docs.json`):

```json
{
  "description": "Nightly documentation update",
  "tasks": [
    {
      "name": "Update READMEs",
      "skill": "readme-generator",
      "group": "production",
      "enabled": true
    },
    {
      "name": "Update PROJECT.md",
      "skill": "repo-summarizer",
      "group": "production",
      "enabled": true
    },
    {
      "name": "Generate journal entries",
      "skill": "journal",
      "group": "all",
      "enabled": true
    }
  ],
  "settings": {
    "parallel": true,
    "max_workers": 5,
    "simple_mode": true,
    "log_file": "~/.orchestrator/logs/nightly.log"
  }
}
```

**2. Run in background:**

```bash
nohup uv run python orchestrator.py --config config/nightly-docs.json &
```

**3. Monitor progress:**

```bash
tail -f ~/.orchestrator/logs/nightly.log
```

**4. Set up cron job:**

```cron
# Update docs every night at 2 AM
0 2 * * * cd /Users/you/workspace/orchestrator && uv run python orchestrator.py --config config/nightly-docs.json
```

## CI/CD Integration

Integrate with GitHub Actions for automated documentation.

**`.github/workflows/docs-update.yml`:**

```yaml
name: Update Documentation

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  update-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install uv
        run: pip install uv

      - name: Run orchestrator
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          uv sync
          uv run python orchestrator.py --config config/ci-docs.json

      - name: Commit changes
        run: |
          git config user.name "Orchestrator Bot"
          git config user.email "bot@example.com"
          git add .
          git commit -m "docs: automated documentation update" || true
          git push
```

## Weekly Status Reports

Generate weekly status reports for all projects.

```bash
# Create weekly journal entries
uv run python orchestrator.py --skill journal --group all

# Analyze GitHub activity
uv run python orchestrator.py --run-agent github-pm-analyzer --days 7
```

## Selective Processing

Process repositories selectively based on tags or groups.

```bash
# Process only Python projects
uv run python orchestrator.py --skill repo-summarizer --tag python

# Process only AI/ML projects
uv run python orchestrator.py --skill code-reviewer --tag ai

# Process experimental projects
uv run python orchestrator.py --skill repo-summarizer --group experimental

# Process specific repos by name
uv run python orchestrator.py --skill readme-generator --repo-names mcp-fleet rishi
```

## Distributed Processing

Process large numbers of repositories across multiple machines.

**Server 1:**
```bash
uv run python orchestrator.py \
  --skill repo-summarizer \
  --repo-names repo1 repo2 repo3 \
  --log-file logs/server1.log
```

**Server 2:**
```bash
uv run python orchestrator.py \
  --skill repo-summarizer \
  --repo-names repo4 repo5 repo6 \
  --log-file logs/server2.log
```

**Server 3:**
```bash
uv run python orchestrator.py \
  --skill repo-summarizer \
  --repo-names repo7 repo8 repo9 \
  --log-file logs/server3.log
```

## Performance Optimization

Optimize execution speed for large batches.

```bash
# Maximum parallelism with simple mode
uv run python orchestrator.py \
  --simple \
  --skill repo-summarizer \
  --group all \
  --max-workers 10

# Sequential processing for debugging
uv run python orchestrator.py \
  --sequential \
  --skill code-reviewer \
  --repo-names problematic-repo
```

## Debugging and Testing

Test skills on individual repositories before batch processing.

```bash
# Test on a single repository
uv run python orchestrator.py \
  --skill new-skill \
  --repos ~/test-repo

# Run in agent mode for detailed output
uv run python orchestrator.py \
  --skill code-reviewer \
  --repos ~/test-repo
  # Note: Agent mode is default, provides detailed iteration logs

# Test with sequential processing
uv run python orchestrator.py \
  --sequential \
  --skill repo-summarizer \
  --repo-names test-repo1 test-repo2
```

## Results and Monitoring

Track and review orchestrator results.

```bash
# Results are saved to ~/orchestrator_{skill-name}_results.json
cat ~/orchestrator_repo-summarizer_results.json

# For batch runs with --config
cat ~/orchestrator_batch_20251201_020000.json

# Monitor logs
tail -f ~/.orchestrator/logs/overnight.log

# Check running processes
ps aux | grep orchestrator
```

## Next Steps

- See [Usage Modes](USAGE_MODES.md) for mode details
- Review [CLI Reference](CLI_REFERENCE.md) for all options
- Read [Autonomous Mode Guide](../AUTONOMOUS_MODE.md) for advanced automation
