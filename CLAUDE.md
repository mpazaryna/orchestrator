# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Overview

This is an **agent-based orchestration system** for coordinating Claude Code workflows. There is no code to build, test, or run - this is a **pure agent coordination framework** using Claude Code's native capabilities.

**Core Architecture**: Natural language → master-orchestrator → specialized agents → external skills → output

**Critical Context**: We previously built a sophisticated Python orchestrator (2,500+ lines) with batch processing, MCP servers, and automation frameworks. We removed all of it because it solved problems we didn't have. See `docs/adr/001-agent-based-orchestration-over-python.md` for the full decision rationale.

## Agent System

### Agent Hierarchy

```
master-orchestrator (top-level router)
├── dev-manager (development workflows)
│   ├── reporter (delegated for 22A reports, devlogs)
│   └── code-review (delegated for code quality)
├── reporter (direct internal comms)
└── code-review (direct quality analysis)
```

All agents are defined in `.claude/agents/*.md` and use natural language delegation patterns.

### Delegation Flow

**User requests trigger automatic agent routing:**

1. User: "Create a 22A report for this project"
2. master-orchestrator analyzes intent → routes to dev-manager
3. dev-manager gathers repo context → delegates to reporter
4. reporter loads `~/workspace/claude-toolkit/generated-skills/internal-comms/`
5. Generated report saved to `docs/reports/22A-YYYY-MM-DD.md`

**Key principle**: Agents delegate, they don't execute directly. The master-orchestrator is a router, not a worker.

## External Skill System

**Critical dependency**: Agents load skills from a centralized toolkit located at:
```
~/workspace/claude-toolkit/generated-skills/
```

**How skills work:**
- Skills are markdown files with prompts/templates
- Agents read skill files using the Read tool
- No copying, no embedding - just file path references
- Skills contain domain-specific knowledge (how to write 22A reports, code review patterns, etc.)

**Key skills referenced:**
- `internal-comms/` - 22A status reports, devlogs
- `code-reviewer/` - Code quality analysis
- `repo-summarizer/` - Project documentation
- `commit-helper/` - Git workflow assistance

**If a skill file is missing**, the agent should fail gracefully and inform the user.

## Repository Configuration

Optional JSON files in `config/` provide metadata:

**`config/repos.json`**: Maps repository names to paths for cross-repo workflows
- Contains 5 active repositories (mcp-fleet, rishi, orchestrator, authentic-advantage, synthetic-notes)
- Groups: "all", "production", "development", "healthcare"
- Used when agents need to work across multiple repositories

**`config/skills.json`**: Maps skill names to toolkit paths
- Reference for locating skills in the external toolkit
- Not required - agents can use direct file paths

**`config/agents.json`**: Metadata about specialized agents
- Describes capabilities and use cases
- Not currently active (Python orchestrator remnant)

## Documentation Structure

**ADRs** (`docs/adr/`): Architecture Decision Records
- ADR-001: Why we chose agents over Python infrastructure (THE critical decision)
- Follow standard ADR format with Context/Problem/Decision/Consequences
- Write new ADRs for significant architectural decisions

**Devlogs** (`docs/devlog/`): Development narratives
- Detailed stories of what happened and what was learned
- Different from ADRs (devlogs = story, ADRs = decision)
- Current: Lessons from Python orchestrator experiment

**Reports** (`docs/reports/`): Generated 22A status reports
- Output location for reporter agent
- Format: `22A-YYYY-MM-DD.md`

**MOC** (`docs/moc/`): Maps of Content
- Project documentation structure

## Custom Slash Commands

**`/git:commit`**: Stage changes and create Conventional Commit
- Uses commit template with Context/Testing/Reviewers sections
- Includes AI attribution footer automatically
- Does NOT push (use `/git:push` separately)

**`/git:push`**: Push current branch to origin
- Verifies commit exists before pushing
- Always confirms branch name first

**`synth-notes`**: Generate synthetic clinical SOAP notes
- Custom command for healthcare data generation
- Delegates to external Python tooling

## Key Principles (From ADR-001)

1. **Simplicity over sophistication**: Agent delegation beats infrastructure
2. **Agents over Python**: Natural language beats code for coordination
3. **Interactive over batch**: Real-time feedback enables iteration
4. **Filesystem as API**: Direct file paths beat configuration systems
5. **Delete confidently**: Remove code that doesn't serve current needs

## Common Workflows

### Generate Status Report
```
User: "Create a 22A report"
→ master-orchestrator → dev-manager → reporter
→ Loads internal-comms skill → Generates docs/reports/22A-YYYY-MM-DD.md
```

### Code Review
```
User: "Review code quality"
→ master-orchestrator → dev-manager → code-review
→ Loads code-reviewer skill → Analyzes and reports findings
```

### Create Devlog
```
User: "Document today's development"
→ master-orchestrator → dev-manager → reporter
→ Analyzes git history → Generates docs/devlog/YYYY-MM-DD-topic.md
```

### Write ADR
```
User: "Document this architectural decision"
→ master-orchestrator → dev-manager → reporter
→ Creates docs/adr/NNN-title.md using ADR template
```

## What NOT to Do

**Don't build Python infrastructure** - We tried this, removed 3,300 lines. Agents work better.

**Don't create batch processing** - Interactive iteration is more valuable than automation.

**Don't copy skills into this repo** - Skills live in `~/workspace/claude-toolkit/`, agents reference them.

**Don't bypass master-orchestrator** - Let the routing logic work. User requests should trigger agents naturally.

**Don't create configuration files** - The existing JSON configs are optional. File paths work fine.

## Troubleshooting

**Agent doesn't activate**: Use trigger words ("use an agent", "help me with", "delegate")

**Skill not found**: Verify path to `~/workspace/claude-toolkit/generated-skills/<skill-name>/`

**Wrong agent delegated**: Update master-orchestrator routing logic in `.claude/agents/master-orchestrator.md`

**Output not saved**: Check agent definitions for expected output paths (usually `docs/reports/` or `docs/devlog/`)

## Historical Context

**November 2025**: Built Python orchestrator with batch processing, MCP servers, parallel execution
**December 1, 2025**: Removed all Python code (-3,300 lines) in favor of agent-based approach
**Rationale**: We were solving theoretical problems (overnight batch jobs, multi-device orchestration) instead of actual problems (interactive skill composition, real-time feedback)

See `docs/adr/001-agent-based-orchestration-over-python.md` for full details.

## Adding New Capabilities

### Add New Agent
1. Create `.claude/agents/new-agent.md` with purpose, tools, triggers
2. Update master-orchestrator routing logic
3. Test with natural language requests
4. Document in README.md

### Add New Skill Reference
1. Skill exists in `~/workspace/claude-toolkit/generated-skills/`
2. Optionally add to `config/skills.json`
3. Reference in agent definitions where needed

### Document Architectural Decision
1. Create `docs/adr/NNN-title.md` using ADR template
2. Update `docs/adr/README.md` with new entry
3. Link from relevant documentation

## Philosophy

**Build for now, not theoretical later.** This project is about learning agent coordination patterns through real usage, not building infrastructure for imaginary scale.
