# Orchestrator - Agent Coordination System

A Claude Code-native agent system for intelligent task delegation and workflow coordination. The master orchestrator analyzes requests and routes them to specialized agents, enabling seamless multi-agent collaboration—all within a Claude Code session, no external infrastructure required.

## Core Concept

**Simple delegation over complex infrastructure. Claude Code sessions ARE the orchestrator.**

This system uses Claude Code's native agent capabilities within a single interactive session to:
- Route requests to appropriate specialized agents
- Load skills from a centralized toolkit
- Coordinate multi-step workflows through natural language
- Provide real-time feedback and iteration

No Python execution. No external infrastructure. Just agent coordination within Claude Code.

## Architecture

```
User Request
    ↓
master-orchestrator (analyzes & routes)
    ↓
Specialized Agents (dev-manager, reporter, code-review)
    ↓
Centralized Skills (~/ workspace/claude-toolkit/generated-skills/)
    ↓
Generated Output
```

## Available Agents

### Master Orchestrator
**Path**: `.claude/agents/master-orchestrator.md`
**Purpose**: Top-level coordinator that analyzes requests and delegates to specialized agents
**Triggers**: "use an agent", "help me with", "delegate"

Routes to:
- **dev-manager** for development workflows, refactoring, implementation
- **reporter** for 22A reports, devlogs, status updates
- **code-review** for formal code quality analysis

### Dev Manager
**Path**: `.claude/agents/dev-manager.md`
**Purpose**: Manages development workflows and delegates to specialized agents
**Capabilities**:
- Code implementation and refactoring
- Repository analysis
- Development documentation
- Delegates to reporter for 22A reports

### Reporter
**Path**: `.claude/agents/reporter.md`
**Purpose**: Generates internal communications and status updates
**Capabilities**:
- 22A status reports
- Devlogs
- Progress documentation
- Loads `internal-comms` skill from toolkit

### Code Review
**Path**: `.claude/agents/code-review.md`
**Purpose**: Formal code quality reviews and best practices analysis
**Capabilities**:
- Code quality assessment
- Security analysis
- Best practices verification
- Loads `code-reviewer` skill from toolkit

## Quick Start

**This system runs entirely within Claude Code sessions - no Python execution, no CLI tools.**

1. Start a Claude Code session in this directory:
```bash
cd ~/workspace/orchestrator
claude
```

2. Make natural language requests - the master-orchestrator activates automatically:
```
"Create a 22A report for this project"
"Use an agent to review code quality"
"Help me document development progress"
```

That's it. All coordination happens through Claude Code's native agent system.

## How It Works

### 1. Natural Language Request
```
> "Create a status report for this project"
```

### 2. Master Orchestrator Analysis
- Identifies intent: status reporting
- Selects appropriate agent: dev-manager
- Determines delegation path: dev-manager → reporter

### 3. Agent Delegation
```
master-orchestrator
  → dev-manager (analyzes repo context)
  → reporter (loads internal-comms skill)
  → generates report at docs/reports/
```

### 4. Real-Time Feedback
- See progress as agents work
- Iterate on output immediately
- No batch jobs or async complexity

## Skill Integration

Agents load skills from the centralized toolkit:

```
~/workspace/claude-toolkit/generated-skills/
  ├── internal-comms/          # 22A reports, status updates
  ├── code-reviewer/           # Code quality analysis
  ├── repo-summarizer/         # Project documentation
  ├── commit-helper/           # Git workflow assistance
  └── ... (10+ other skills)
```

**No copying, no embedding, just file paths.**

## Example Workflows

### Generate a Status Report
```
> "Create a 22A report for orchestrator"

master-orchestrator analyzes request
  → Routes to dev-manager
  → dev-manager analyzes repo
  → Delegates to reporter
  → reporter loads internal-comms skill
  → Generates report at docs/reports/22A-YYYY-MM-DD.md
```

### Code Review Request
```
> "Review code quality in src/"

master-orchestrator analyzes request
  → Routes to dev-manager
  → dev-manager delegates to code-review
  → code-review loads code-reviewer skill
  → Analyzes code structure and quality
  → Returns findings to user
```

### Development Documentation
```
> "Document today's development progress"

master-orchestrator analyzes request
  → Routes to dev-manager
  → dev-manager analyzes git history
  → Delegates to reporter for devlog
  → reporter generates devlog
  → Saves to docs/devlog/
```

## Configuration

### Repository Config (Optional)
`config/repos.json` - Define repositories for cross-repo workflows
```json
{
  "repositories": [
    {
      "name": "orchestrator",
      "path": "/Users/mpaz/workspace/orchestrator",
      "active": true,
      "tags": ["development", "ai-tools"]
    }
  ]
}
```

### Skills Config (Optional)
`config/skills.json` - Map skills in your toolkit
```json
{
  "skills": [
    {
      "name": "internal-comms",
      "path": "/Users/mpaz/workspace/claude-toolkit/generated-skills/internal-comms",
      "description": "Generate 22A reports and status updates"
    }
  ]
}
```

**Note**: These configs are optional. Agents can work with direct file paths.

## Why This Approach?

### What We Tried Before
We built a sophisticated Python orchestrator with:
- Batch processing engines
- Parallel execution frameworks
- MCP server infrastructure
- Task configuration systems
- 2500+ lines of automation code

**We removed all of it (-3,300 lines total) in December 2025.**

### What We Learned
**We were solving problems we didn't have.**

The Claude Code-native agent approach is:
- ✅ **Simpler**: No code to run, no dependencies, no infrastructure
- ✅ **More effective**: Real-time iteration within Claude Code beats batch jobs
- ✅ **More maintainable**: 200 lines of agent config vs 2500 lines of Python
- ✅ **More natural**: Natural language delegation beats orchestration code
- ✅ **More focused**: Solve actual workflow problems, not theoretical scale

**Critical insight**: Claude Code sessions *are* the orchestrator. We don't need to build one.

See: `docs/devlog/2025-12-01-python-orchestrator-lessons.md` and `docs/adr/001-agent-based-orchestration-over-python.md` for the full story.

## Project Structure

```
orchestrator/
├── .claude/
│   └── agents/              # Agent definitions
│       ├── master-orchestrator.md
│       ├── dev-manager.md
│       ├── reporter.md
│       └── code-review.md
├── config/                  # Optional configuration
│   ├── repos.json          # Repository definitions
│   └── skills.json         # Skill mappings
├── docs/
│   ├── devlog/             # Development logs
│   ├── reports/            # Generated 22A reports
│   └── guide/              # Usage guides
├── README.md               # This file
└── PROJECT.md              # Project portfolio documentation
```

## Development Workflow

### Adding a New Agent

1. Create agent file: `.claude/agents/your-agent.md`
2. Define purpose, tools, and delegation patterns
3. Update master-orchestrator routing logic
4. Test with natural language requests

### Adding a New Skill

1. Add skill to toolkit: `~/workspace/claude-toolkit/generated-skills/`
2. Optionally add to `config/skills.json`
3. Reference in agent definitions
4. Test delegation workflow

### Improving Delegation

1. Monitor agent interactions
2. Identify routing inefficiencies
3. Update master-orchestrator logic
4. Document patterns in agent files

## Documentation

- **Getting Started**: This README
- **Architecture Decisions**: `docs/devlog/2025-12-01-python-orchestrator-lessons.md`
- **Agent Definitions**: `.claude/agents/*.md`
- **Project Overview**: `PROJECT.md`

## Key Principles

1. **Simplicity over sophistication**: Choose the simplest solution that works
2. **Agents over infrastructure**: Delegation beats automation frameworks
3. **Interactive over batch**: Real-time feedback enables better iteration
4. **Natural over configured**: Natural language beats JSON configs
5. **Delete confidently**: Remove code that doesn't serve current needs

## License

MIT License - See LICENSE.txt for details

---

**Status**: Active development - Agent-based coordination system
**Last Updated**: December 1, 2025
**Philosophy**: Build for now, not theoretical later
