# Autonomous Mode

Run the orchestrator unattended for overnight processing, cron jobs, or distributed execution.

## Quick Start

```bash
# Run task configuration in background
nohup uv run python orchestrator.py --config config/overnight.json &

# Check progress
tail -f ~/.orchestrator/logs/overnight.log
```

## Task Configuration Format

Create a JSON file defining tasks to run:

```json
{
  "description": "What this batch does",
  "tasks": [
    {
      "name": "Task description",
      "skill": "skill-name",
      "group": "all",           // or "tag", "repos", "repo_names"
      "enabled": true
    }
  ],
  "settings": {
    "parallel": true,           // Run repos in parallel
    "max_workers": 5,          // Max concurrent repos
    "simple_mode": true,       // Fast mode (single API call per repo)
    "log_file": "~/.orchestrator/logs/run.log"
  }
}
```

## Common Patterns

### Overnight Documentation Update

**config/overnight.json:**
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

**Run it:**
```bash
nohup uv run python orchestrator.py --config config/overnight.json &
```

### Cron Job (Daily Updates)

```cron
# Update docs every night at 2 AM
0 2 * * * cd /Users/mpaz/workspace/orchestrator && uv run python orchestrator.py --config config/overnight.json
```

### Distributed Execution

Run different repos on different machines:

**server1:**
```bash
uv run python orchestrator.py \
  --skill repo-summarizer \
  --repo-names mcp-fleet rishi \
  --log-file logs/server1.log
```

**server2:**
```bash
uv run python orchestrator.py \
  --skill repo-summarizer \
  --repo-names orchestrator synthetic-notes \
  --log-file logs/server2.log
```

### CI/CD Integration

**GitHub Actions:**
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
          uv run python orchestrator.py --config config/overnight.json

      - name: Commit changes
        run: |
          git config user.name "Orchestrator Bot"
          git config user.email "bot@example.com"
          git add .
          git commit -m "docs: automated documentation update" || true
          git push
```

## Repository Selection

Tasks can target repos by:

**Group:**
```json
{"skill": "readme-generator", "group": "production"}
```

**Tag:**
```json
{"skill": "code-reviewer", "tag": "python"}
```

**Specific paths:**
```json
{"skill": "journal", "repos": ["/path/to/repo1", "/path/to/repo2"]}
```

**Repo names from config:**
```json
{"skill": "repo-summarizer", "repo_names": ["mcp-fleet", "rishi"]}
```

## Logging

**To file (for background runs):**
```bash
uv run python orchestrator.py --config tasks.json --log-file logs/run.log
```

**To stdout (for debugging):**
```bash
uv run python orchestrator.py --config tasks.json
```

**Settings in config override CLI:**
```json
{
  "settings": {
    "log_file": "~/.orchestrator/logs/overnight.log"
  }
}
```

## Monitoring

**Watch logs:**
```bash
tail -f ~/.orchestrator/logs/overnight.log
```

**Check results:**
```bash
ls -lt ~/orchestrator_batch_*.json | head -5
cat ~/orchestrator_batch_20251201_020000.json
```

**Process status:**
```bash
ps aux | grep orchestrator
```

**Kill running orchestrator:**
```bash
pkill -f "python orchestrator.py"
```

## Simple Mode vs Agent Mode

**Simple Mode (Recommended for autonomous runs):**
- Single API call per repo
- Fast (~30-60 seconds per repo)
- Deterministic output
- Lower cost

```json
{"settings": {"simple_mode": true}}
```

**Agent Mode:**
- Multiple iterations with tool use
- Slower (~2-5 minutes per repo)
- More thorough analysis
- Higher cost

```json
{"settings": {"simple_mode": false}}
```

## Error Handling

**Failed tasks continue processing:**
- Each task runs independently
- Failures logged but don't stop execution
- Check results JSON for error details

**Example error in results:**
```json
{
  "repo": "mcp-fleet",
  "status": "error",
  "message": "Path does not exist",
  "skill": "readme-generator"
}
```

## Best Practices

1. **Test interactively first:**
   ```bash
   # Test before running overnight
   uv run python orchestrator.py --skill readme-generator --repos ~/test-repo
   ```

2. **Use simple mode for batch:**
   - Faster
   - More predictable
   - Lower cost

3. **Enable only needed tasks:**
   ```json
   {"enabled": false}  // Skip this task
   ```

4. **Monitor logs initially:**
   - Watch first few runs
   - Verify output quality
   - Adjust configs as needed

5. **Separate task configs:**
   - `overnight.json` - Full documentation update
   - `quick.json` - Fast checks
   - `production.json` - Production repos only

## Examples

See `config/` directory:
- `tasks.example.json` - Template with all options
- `overnight.json` - Overnight documentation run
