# ADR 001: Agent-Based Orchestration Over Python Infrastructure

**Date**: 2025-12-01
**Status**: Accepted
**Deciders**: Development Team
**Technical Story**: Simplification of orchestration architecture

## Context

We initially built a sophisticated Python-based orchestrator to run Claude skills across multiple repositories. The implementation included:

- **Batch processing engine** with parallel execution (ThreadPoolExecutor)
- **Autonomous agent runner** with tool-based execution
- **FastMCP server** exposing Python agents as tools
- **Configuration management system** (repos.json, skills.json, agents.json)
- **Interactive menu system** for CLI workflows
- **Task configuration framework** for overnight/cron jobs
- **~2,500 lines of Python code** plus ~800 lines of tests

The stated goals were:
1. Run skills from centralized toolkit (`~/workspace/claude-toolkit/generated-skills/`)
2. Process multiple repositories efficiently
3. Support unattended batch execution
4. Provide professional workflow automation

While developing this infrastructure, we discovered Claude Code's native agent system and began experimenting with agent delegation patterns.

## Problem

The Python orchestrator solved **problems we don't have**:

### Assumed Requirements (Not Actual)
- ❌ Processing 100s of repositories in parallel
- ❌ Multi-device distributed orchestration
- ❌ Overnight batch jobs and cron automation
- ❌ Complex task scheduling and dependency management
- ❌ Heavy Python agent logic requiring dedicated infrastructure

### Actual Requirements
- ✅ Interactive skill composition and iteration
- ✅ Access to centralized skill library
- ✅ Multi-step workflow coordination
- ✅ Report generation and documentation
- ✅ Real-time feedback during development

### Architecture Complexity

The Python solution had 4 abstraction layers:
```
CLI Interface
    ↓
Orchestrator Core (skill loading, context)
    ↓
Execution Router (simple vs agent mode)
    ↓
Agent Runner → Tool Executor → File Operations
```

This complexity:
- **Obscured value**: Infrastructure overhead hid the actual workflow patterns
- **Slowed iteration**: Required Python expertise to modify behavior
- **Created maintenance burden**: Dependencies, testing, deployment
- **Prevented learning**: Couldn't experiment with delegation patterns easily

## Decision

**We will use Claude Code's native agent system instead of Python infrastructure.**

### New Architecture

Single-layer delegation:
```
User Request
    ↓
master-orchestrator (analyzes & routes)
    ↓
Specialized Agents (dev-manager, reporter, code-review)
    ↓
Skills (loaded from ~/workspace/claude-toolkit/generated-skills/)
    ↓
Generated Output
```

### Implementation

**Agent Definitions** (`.claude/agents/*.md`):
- `master-orchestrator.md` - Top-level request router
- `dev-manager.md` - Development workflow coordinator
- `reporter.md` - Internal communications generator
- `code-review.md` - Code quality analyzer

**Skill Access**:
- Direct file path references to toolkit
- No copying, embedding, or infrastructure
- Skills loaded on-demand via Read tool

**Workflow**:
```
User: "Create a 22A report for this project"
  → master-orchestrator (analyzes request)
  → dev-manager (gathers repo context)
  → reporter (loads internal-comms skill)
  → Generated report saved to docs/reports/
```

## Consequences

### Positive

**Simplicity**
- ✅ Zero setup required (no dependencies, no installation)
- ✅ 200 lines of agent config vs 2,500 lines of Python
- ✅ Single-layer architecture vs 4-layer complexity
- ✅ Natural language interface vs CLI flags/JSON configs

**Effectiveness**
- ✅ Real-time iteration and feedback
- ✅ Transparent execution (see agent reasoning)
- ✅ Easy to modify and experiment
- ✅ Works in actual development context

**Maintainability**
- ✅ No dependencies to manage
- ✅ No test infrastructure required
- ✅ Self-documenting (agent definitions are docs)
- ✅ Version controlled in markdown

**Focus**
- ✅ Solve actual workflow problems
- ✅ Learn delegation patterns
- ✅ Improve agent coordination
- ✅ Refine skill design

### Negative

**Lost Capabilities** (that we don't need):
- ❌ Batch processing across many repos
- ❌ Parallel execution optimization
- ❌ Unattended overnight runs
- ❌ MCP tool exposure for Python agents

**Trade-offs**:
- Manual iteration vs automated batch (acceptable - we prefer interactive)
- Claude Code dependency vs standalone tool (acceptable - we use Claude Code)
- Sequential vs parallel (acceptable - we process 1-3 repos at a time)

### Migration

**Removed**:
- `src/orchestrator/` - Python package (~2,500 lines)
- `src/mcp/` - MCP server infrastructure
- `tests/` - Test framework (~800 lines)
- `docs/guide/` - Python CLI documentation
- `pyproject.toml`, `uv.lock` - Dependencies
- Task configuration files

**Kept**:
- `config/repos.json` - Repository definitions (may be useful for agents)
- `config/skills.json` - Skill mappings (reference for file paths)
- Agent definitions - Core of new architecture

**Documented**:
- This ADR - Architectural decision rationale
- `docs/devlog/2025-12-01-python-orchestrator-lessons.md` - Detailed lessons learned
- Updated README.md - Agent-based approach

## Lessons Learned

### About Premature Optimization

**Build for now, not theoretical later.**
- We optimized for scale we don't have
- We automated workflows we don't run
- We built infrastructure we don't need

### About Simplicity

**The filesystem is underrated.**
- File paths work fine as an API
- No need for configuration systems
- Direct access beats abstraction layers

### About Tools

**Agents > Infrastructure.**
- Composition beats automation frameworks
- Natural language beats JSON configs
- Interactive beats batch for learning

### About Engineering Judgment

**Deleting code is a win.**
- Removing 3,300 lines while retaining all value
- Having the courage to abandon sophisticated code
- Recognizing over-engineering and course-correcting

## References

- Python implementation: Removed (see git history)
- Detailed retrospective: `docs/devlog/2025-12-01-python-orchestrator-lessons.md`
- Agent definitions: `.claude/agents/master-orchestrator.md`, `dev-manager.md`, `reporter.md`, `code-review.md`
- Updated architecture: `README.md`

## Related Decisions

- None (first ADR)

## Notes

This decision should be celebrated as excellent engineering:
1. We built something sophisticated
2. We learned it was over-engineered
3. We found a better solution
4. We had the courage to delete it

The Python orchestrator was not wasted effort - it taught us what we actually need.

---

**Status**: Accepted and implemented (December 1, 2025)
**Impact**: -3,300 lines of code, +100% clarity on value proposition
