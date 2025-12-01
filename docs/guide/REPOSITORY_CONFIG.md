# Repository Configuration

Configure your repositories in `repos.json` for organized batch processing.

## Basic Structure

```json
{
  "repositories": [
    {
      "name": "project-name",
      "path": "/absolute/path/to/repo",
      "github": "https://github.com/user/project",
      "description": "Brief description",
      "tags": ["tag1", "tag2"],
      "active": true
    }
  ],
  "groups": {
    "group-name": ["project1", "project2"]
  }
}
```

## Repository Fields

### Required Fields

- **name**: Unique identifier for the repository (used in --repo-names)
- **path**: Absolute path to repository on your filesystem
- **active**: Boolean - whether to include in "all" group queries

### Optional Fields

- **github**: GitHub URL for reference
- **description**: Brief description of the repository
- **tags**: Array of tags for filtering (used with --tag)

## Groups

Groups allow you to organize repositories into logical collections:

```json
{
  "groups": {
    "all": ["repo1", "repo2", "repo3"],
    "production": ["repo1", "repo2"],
    "experimental": ["repo3"],
    "python": ["repo1", "repo3"],
    "typescript": ["repo2"]
  }
}
```

Usage:

```bash
# Process all production repos
uv run python orchestrator.py --group production

# Process all Python repos
uv run python orchestrator.py --group python
```

## Tags

Tags provide flexible filtering across repositories:

```json
{
  "repositories": [
    {
      "name": "web-app",
      "tags": ["web", "production", "typescript"],
      "active": true
    },
    {
      "name": "ml-service",
      "tags": ["ai", "python", "experimental"],
      "active": true
    }
  ]
}
```

Usage:

```bash
# Process all repos with "ai" tag
uv run python orchestrator.py --tag ai

# Process all repos with "production" tag
uv run python orchestrator.py --tag production
```

## Example Configuration

```json
{
  "repositories": [
    {
      "name": "mcp-fleet",
      "path": "/Users/you/workspace/mcp-fleet",
      "github": "https://github.com/you/mcp-fleet",
      "description": "MCP server orchestration toolkit",
      "tags": ["python", "mcp", "production"],
      "active": true
    },
    {
      "name": "orchestrator",
      "path": "/Users/you/workspace/orchestrator",
      "github": "https://github.com/you/orchestrator",
      "description": "Generic orchestrator for Claude skills",
      "tags": ["python", "automation", "production"],
      "active": true
    },
    {
      "name": "experimental-ai",
      "path": "/Users/you/workspace/experimental-ai",
      "github": "https://github.com/you/experimental-ai",
      "description": "AI experiments and prototypes",
      "tags": ["python", "ai", "experimental"],
      "active": false
    }
  ],
  "groups": {
    "all": ["mcp-fleet", "orchestrator"],
    "production": ["mcp-fleet", "orchestrator"],
    "experimental": ["experimental-ai"],
    "python": ["mcp-fleet", "orchestrator", "experimental-ai"]
  }
}
```

## Verification

List configured repositories:

```bash
uv run python orchestrator.py --list-repos
```

List repository groups:

```bash
uv run python orchestrator.py --list-groups
```

## Best Practices

1. **Use absolute paths**: Relative paths may not work across different execution contexts
2. **Keep active current**: Set `active: false` for archived or inactive repos
3. **Organize with groups**: Create logical groups for your workflow (production, experimental, etc.)
4. **Tag consistently**: Use consistent tag names across repos for easier filtering
5. **Update regularly**: Keep descriptions and GitHub URLs current for reference

## Next Steps

- Learn about [Usage Modes](USAGE_MODES.md)
- See [Example Workflows](EXAMPLES.md)
