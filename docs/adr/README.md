# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for the orchestrator project.

## What is an ADR?

An Architecture Decision Record (ADR) captures an important architectural decision made along with its context and consequences. ADRs help teams:

- **Understand why** decisions were made
- **Track evolution** of the system over time
- **Onboard new team members** by providing historical context
- **Avoid revisiting** settled decisions
- **Learn from** past choices (good and bad)

## Format

Each ADR follows this structure:

```markdown
# ADR NNN: Brief Title

**Date**: YYYY-MM-DD
**Status**: [Proposed | Accepted | Deprecated | Superseded]
**Deciders**: Who made the decision
**Technical Story**: Brief context

## Context
What is the issue we're facing? What factors are we considering?

## Problem
What problem are we trying to solve? What are the constraints?

## Decision
What are we going to do? What is the change we're making?

## Consequences
What becomes easier or harder as a result of this decision?
```

## Naming Convention

- `NNN-title-with-dashes.md`
- Numbers are sequential: `001`, `002`, `003`, etc.
- Titles are lowercase with dashes
- Examples:
  - `001-agent-based-orchestration-over-python.md`
  - `002-use-markdown-for-skill-definitions.md`
  - `003-centralize-toolkit-location.md`

## Status Lifecycle

- **Proposed**: Decision under consideration
- **Accepted**: Decision is approved and implemented
- **Deprecated**: Decision is no longer relevant
- **Superseded**: Replaced by a newer ADR (reference the new ADR)

## When to Write an ADR

Create an ADR when you:

- Make a significant architectural choice
- Choose between multiple valid approaches
- Adopt or abandon a technology/pattern
- Significantly refactor the system
- Make a decision that affects future development

Examples from this project:
- Choosing agent-based over Python infrastructure (ADR-001)
- Selecting skill definition format
- Deciding on delegation patterns
- Standardizing documentation structure

## Current ADRs

1. [ADR-001: Agent-Based Orchestration Over Python](001-agent-based-orchestration-over-python.md) - **Accepted**
   - Architectural shift from Python infrastructure to Claude Code agents
   - Rationale for simplification and removal of 3,300 lines of code

## Template

```markdown
# ADR NNN: Title Here

**Date**: YYYY-MM-DD
**Status**: Proposed
**Deciders**: [Names or "Development Team"]
**Technical Story**: [Brief context]

## Context

[Describe the forces at play, the current situation, and what led to this decision point]

## Problem

[What specific problem are we solving? What are the constraints?]

## Decision

[What are we going to do? Be specific and concrete]

## Consequences

### Positive
- ✅ [What becomes easier]

### Negative
- ❌ [What becomes harder]

### Trade-offs
- [Accepted compromises]

## References

- [Links to related docs, code, or discussions]

## Related Decisions

- [Links to other ADRs that relate to this one]
```

## Best Practices

1. **Write ADRs at decision time**, not retroactively
   - Exception: ADR-001 was written when abandoning Python (still fresh)

2. **Keep them concise** but comprehensive
   - Focus on why, not just what
   - Include enough context for future readers

3. **Link to detailed docs** rather than duplicating
   - ADRs are decisions, devlogs are stories

4. **Update status** as decisions evolve
   - Mark as Deprecated when no longer relevant
   - Reference superseding ADRs

5. **Don't change past ADRs** (except status/typos)
   - ADRs are historical records
   - Write new ADRs to supersede old ones

## Resources

- [Architecture Decision Records](https://adr.github.io/) - General ADR information
- [ADR Tools](https://github.com/npryce/adr-tools) - Command-line tools for ADRs
- [When to Write an ADR](https://engineering.atspotify.com/2020/04/when-should-i-write-an-architecture-decision-record/)

---

**Note**: This is a living document. As we adopt ADR practices, we may refine this format based on what works for our team.
