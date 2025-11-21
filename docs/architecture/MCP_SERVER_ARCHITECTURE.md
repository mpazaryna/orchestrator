# Orchestrator MCP Server Architecture

**Date**: 2025-11-21
**Version**: 1.0.0
**Status**: Production

## Executive Summary

The Orchestrator MCP Server is a universal agent platform that exposes all business tools, agents, and automation capabilities through a single Model Context Protocol (MCP) interface. This enables any Claude-powered client—CLI, IDE, web app, or custom integration—to access the full suite of organizational capabilities through natural language.

**Key Value Proposition**: Write agents once, access them everywhere, in any context.

---

## The Problem

### Before: Fragmented Tooling

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Developer Workflow                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Repo A          Repo B          Repo C          Standalone        │
│   ┌─────┐         ┌─────┐         ┌─────┐         ┌─────────┐      │
│   │CLI  │         │CLI  │         │CLI  │         │Scripts  │      │
│   │tools│         │tools│         │tools│         │         │      │
│   └─────┘         └─────┘         └─────┘         └─────────┘      │
│      │               │               │                 │            │
│      ▼               ▼               ▼                 ▼            │
│   Different      Different      Different         Manual           │
│   commands       syntax         configs           execution        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Problems:
- Context switching between repos
- Remembering different CLI syntaxes
- Tools not accessible outside their repo
- No composition between tools
- Manual orchestration required
```

### After: Unified Agent Platform

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Orchestrator MCP Server                         │
│                    (Single Source of Truth)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   agents.json ────► All registered agents                           │
│   skills.json ────► All registered skills                           │
│   tools/*.py  ────► MCP tool definitions                            │
│                                                                     │
│   Exposed Tools:                                                    │
│   • generate_soap_notes      • sync_github_repos                    │
│   • list_agents              • collect_github_issues                │
│   • list_skills              • run_trend_analysis                   │
│   • (any future agent)       • (any future tool)                    │
│                                                                     │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ MCP Protocol
                                 │
         ┌───────────┬───────────┼───────────┬───────────┐
         │           │           │           │           │
         ▼           ▼           ▼           ▼           ▼
    Claude Code   VS Code     Web App    Slack Bot   Custom
    (any repo)    + Claude    React UI   Integration  Client
```

---

## Architecture Overview

### Layer Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
│                                                                     │
│   Claude Code    VS Code      Web UI      Mobile      Slack/Teams   │
│   (Terminal)     (IDE)        (React)     (Future)    (Future)      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ MCP Protocol (stdio/http/websocket)
                                 │
┌────────────────────────────────┴────────────────────────────────────┐
│                      MCP SERVER LAYER                               │
│                                                                     │
│   server.py ─────► FastMCP server instance                          │
│                    • Tool registration                              │
│                    • Request routing                                │
│                    • Response formatting                            │
│                                                                     │
│   tools/ ────────► Modular tool definitions                         │
│                    • synth_notes/                                   │
│                    • github_pm/                                     │
│                    • research/                                      │
│                    • content/                                       │
│                                                                     │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ Python imports
                                 │
┌────────────────────────────────┴────────────────────────────────────┐
│                    ORCHESTRATOR LAYER                               │
│                                                                     │
│   orchestrator.py ──► Execution engine                              │
│   config.py ────────► Configuration management                      │
│   python_agent_runner.py ──► Agent instantiation                    │
│                                                                     │
│   config/ ──────────► Registry files                                │
│                       • agents.json                                 │
│                       • skills.json                                 │
│                       • repos.json                                  │
│                                                                     │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ Dynamic loading
                                 │
┌────────────────────────────────┴────────────────────────────────────┐
│                      AGENT LAYER                                    │
│                                                                     │
│   claude-toolkit/generated-agents/                                  │
│   ├── synth-notes-generator/                                        │
│   │   └── agent.py ──► SynthNotesAgent class                        │
│   ├── research-agent/                                               │
│   │   └── agent.py ──► ResearchAgent class                          │
│   ├── competitor-analyzer/                                          │
│   │   └── agent.py ──► CompetitorAgent class                        │
│   └── ...                                                           │
│                                                                     │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ External APIs / File System
                                 │
┌────────────────────────────────┴────────────────────────────────────┐
│                     EXTERNAL LAYER                                  │
│                                                                     │
│   Anthropic API ──► LLM calls for generation                        │
│   GitHub API ─────► Repository and issue data                       │
│   File System ────► Reading/writing outputs                         │
│   Databases ──────► Supabase, local storage                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **MCP Server** | Protocol handling, tool exposure, request/response |
| **Tool Modules** | Define MCP tools, validate inputs, format outputs |
| **Orchestrator** | Execution engine, agent lifecycle, configuration |
| **Agents** | Autonomous task execution, API calls, file operations |
| **Config** | Registry of available agents, skills, repositories |

---

## Tool Module Structure

### Directory Layout

```
src/mcp/
├── server.py                    # Main server, imports tool modules
├── __init__.py
└── tools/
    ├── __init__.py
    │
    ├── synth_notes/             # Clinical data generation
    │   ├── __init__.py
    │   └── generate.py          # generate_soap_notes, list_soap_prompt_types
    │
    ├── github_pm/               # GitHub project management
    │   ├── __init__.py
    │   ├── sync.py              # sync_github_repos
    │   ├── collect.py           # collect_github_issues
    │   └── analysis.py          # run_trend_analysis, run_commit_analysis
    │
    ├── research/                # Web research and documentation
    │   ├── __init__.py
    │   ├── web_research.py      # research_topic, fetch_documentation
    │   └── competitor.py        # analyze_competitors
    │
    └── content/                 # Content generation
        ├── __init__.py
        ├── blog.py              # write_blog_post
        ├── social.py            # write_linkedin_post, write_twitter_thread
        └── email.py             # draft_email, write_newsletter
```

### Tool Registration Pattern

Each tool module exports a `register_tools` function:

```python
# tools/synth_notes/generate.py

def register_tools(mcp: FastMCP, config_loader, python_runner):
    """Register synth-notes tools with the MCP server."""

    @mcp.tool()
    def generate_soap_notes(
        prompt_type: str,
        total: int = 10,
        batch_size: int = 2
    ) -> dict:
        """
        Generate synthetic clinical SOAP notes for training datasets.

        Args:
            prompt_type: Clinical scenario type
            total: Number of notes to generate
            batch_size: Notes per API call

        Returns:
            dict with batch_folder, notes_generated, usage stats
        """
        agent_config = config_loader.get_agent("synth-notes-generator")
        result = python_runner.run_agent(
            agent_config=agent_config.__dict__,
            task_config={
                "prompt_type": prompt_type,
                "total": total,
                "batch_size": batch_size
            }
        )
        return result
```

Server imports and registers:

```python
# server.py

from tools.synth_notes import register_tools as register_synth_notes
from tools.github_pm import register_tools as register_github_pm

register_synth_notes(mcp, config_loader, python_runner)
register_github_pm(mcp, config_loader, python_runner)
```

---

## Use Cases

### Use Case 1: Cross-Project Development

**Scenario**: Developer working in a web application repo needs test data.

```
┌─────────────────────────────────────────────────────────────────────┐
│  VS Code: ~/workspace/chiro-page                                    │
│  (Chiropractic patient management app)                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Developer: "I need 20 neck pain SOAP notes to test my parser"      │
│                                                                     │
│  Claude (via MCP):                                                  │
│    1. Calls generate_soap_notes(prompt_type="adult_neck_pain",      │
│       total=20) via orchestrator MCP                                │
│    2. Agent generates notes to synthetic-notes/output/batch_007/    │
│    3. Uses native file tools to read the generated notes            │
│    4. Creates test file in chiro-page/tests/fixtures/               │
│    5. Updates test suite to use new fixtures                        │
│                                                                     │
│  Result: Test data generated and integrated without leaving IDE     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Key Insight**: Claude's native abilities (file read/write, code understanding) compose with MCP tools (data generation). Neither could accomplish this alone.

### Use Case 2: Multi-Repository Analysis

**Scenario**: Team lead needs weekly status across all projects.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Claude Code: ~/workspace (any location)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Lead: "Give me a summary of activity across all my GitHub repos    │
│         this week, and flag any issues that need attention"         │
│                                                                     │
│  Claude (via MCP):                                                  │
│    1. Calls sync_github_repos() → gets current repo list            │
│    2. Calls collect_github_issues() → gathers all open issues       │
│    3. Calls run_trend_analysis(baseline="2025-11-14",               │
│       current="2025-11-21") → compares activity                     │
│    4. Synthesizes results into executive summary                    │
│    5. Highlights blockers, stale issues, velocity changes           │
│                                                                     │
│  Result: Comprehensive status report from natural language request  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Use Case 3: Content Pipeline

**Scenario**: Marketing needs consistent content across channels.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Web UI: company-tools.internal/agents                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Marketing: "Write a blog post about our new feature, then create   │
│              a LinkedIn summary and tweet thread to promote it"     │
│                                                                     │
│  Claude (via MCP):                                                  │
│    1. Calls write_blog_post(topic="new feature",                    │
│       tone="professional", length="1500 words")                     │
│    2. Calls write_linkedin_post(source="blog",                      │
│       style="thought leadership")                                   │
│    3. Calls write_twitter_thread(source="blog", max_tweets=5)       │
│    4. Returns all content for review                                │
│                                                                     │
│  Result: Consistent messaging across all channels                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Use Case 4: Competitive Intelligence

**Scenario**: Product team needs competitor analysis.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Claude Code: ~/workspace/product-strategy                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PM: "Research our top 3 competitors' recent product launches       │
│       and summarize their positioning"                              │
│                                                                     │
│  Claude (via MCP):                                                  │
│    1. Calls research_competitors(companies=["CompA", "CompB",       │
│       "CompC"], focus="product launches", timeframe="90 days")      │
│    2. Agent fetches press releases, blog posts, social media        │
│    3. Synthesizes into competitive analysis report                  │
│    4. Saves to product-strategy/research/competitor-analysis.md    │
│                                                                     │
│  Result: Research automated, findings in version control            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Use Case 5: Enterprise Deployment

**Scenario**: Organization wants all staff to have agent access.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Enterprise Architecture                                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                    ┌─────────────────────────┐                      │
│                    │  Orchestrator MCP Server │                     │
│                    │  (Central deployment)    │                     │
│                    │                          │                     │
│                    │  • All company agents    │                     │
│                    │  • Auth/permissions      │                     │
│                    │  • Usage tracking        │                     │
│                    │  • Cost management       │                     │
│                    └────────────┬─────────────┘                     │
│                                 │                                   │
│          ┌──────────┬──────────┼──────────┬──────────┐             │
│          │          │          │          │          │             │
│          ▼          ▼          ▼          ▼          ▼             │
│      Engineer    Designer    PM       Marketing   Support          │
│      (IDE)       (Figma?)   (Web)     (Slack)    (Zendesk?)       │
│                                                                     │
│  Each role gets:                                                    │
│  • Same agent capabilities                                          │
│  • Role-appropriate interface                                       │
│  • Unified billing/tracking                                         │
│  • No training required ("just ask")                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Why This Matters

### 1. Context Independence

Tools work regardless of where you call them from:

| Location | Same Tools Available |
|----------|---------------------|
| `~/workspace/chiro-page` | ✅ All agents |
| `~/workspace/synthetic-notes` | ✅ All agents |
| `~/workspace/mcp-fleet` | ✅ All agents |
| Remote server via SSH | ✅ All agents |
| Web browser | ✅ All agents |

### 2. Composability

MCP tools compose with Claude's native abilities:

```
Native Claude          +    MCP Tools           =    Powerful Workflows
─────────────────────       ────────────────         ────────────────────
• Read/write files          • Generate data          • Generate test data
• Understand code           • Fetch research           and integrate it
• Run commands              • Analyze repos          • Research and write
• Edit code                 • Create content           documentation
                                                     • Analyze code and
                                                       create reports
```

### 3. Single Source of Truth

One place to manage all capabilities:

```
agents.json
├── Add new agent ──────► Immediately available everywhere
├── Update agent ───────► All clients get new version
└── Remove agent ───────► Clean deprecation

No:
• Multiple deployments
• Version mismatches
• Training updates
• Documentation sprawl
```

### 4. Natural Language Interface

Users don't need to know:
- CLI syntax
- Configuration files
- Which repo to be in
- How tools are implemented

They just say what they want:

> "Generate clinical training data"
> "Summarize my GitHub activity"
> "Research competitor pricing"

### 5. Cost Transparency

All agent usage flows through one server:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Usage Dashboard                                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Agent                    │ Calls │ Tokens    │ Cost    │ Trend    │
│  ─────────────────────────┼───────┼───────────┼─────────┼───────── │
│  synth-notes-generator    │   47  │ 1.2M      │ $18.50  │ ↑ 12%    │
│  research-agent           │   23  │ 890K      │ $12.30  │ → 0%     │
│  competitor-analyzer      │    8  │ 340K      │ $5.10   │ ↓ 5%     │
│  ─────────────────────────┼───────┼───────────┼─────────┼───────── │
│  Total                    │   78  │ 2.4M      │ $35.90  │           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Deployment Options

### Option 1: Local Development

```bash
# Start server (runs in background or dedicated terminal)
cd ~/workspace/orchestrator
uv run python src/mcp/server.py

# Or via stdio (auto-started by Claude Code)
# .mcp.json in any project points to orchestrator
```

**Best for**: Individual developer, local machine

### Option 2: Persistent Service

```bash
# systemd service or launchd plist
# Auto-starts on boot, restarts on failure

[Unit]
Description=Orchestrator MCP Server
After=network.target

[Service]
ExecStart=/usr/bin/uv run python src/mcp/server.py --transport http --port 8080
WorkingDirectory=/home/user/workspace/orchestrator
Restart=always

[Install]
WantedBy=multi-user.target
```

**Best for**: Power user, multiple machines

### Option 3: Docker Container

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync
EXPOSE 8080
CMD ["uv", "run", "python", "src/mcp/server.py", "--transport", "http", "--port", "8080"]
```

**Best for**: Team deployment, consistent environment

### Option 4: Cloud Deployment

```yaml
# fly.io, Railway, or similar
app: orchestrator-mcp
env:
  ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}

services:
  - port: 8080
    protocol: tcp
```

**Best for**: Enterprise, multi-user access

---

## Security Considerations

### API Key Management

```
┌─────────────────────────────────────────────────────────────────────┐
│  API Keys flow through MCP server, not clients                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Client ──► MCP Server ──► Anthropic API                            │
│             (has key)      (authenticated)                          │
│                                                                     │
│  Benefits:                                                          │
│  • Keys never exposed to end users                                  │
│  • Central rotation                                                 │
│  • Usage attribution                                                │
│  • Rate limiting per user                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Access Control (Future)

```python
@mcp.tool(requires_role=["admin", "developer"])
def dangerous_operation():
    ...

@mcp.tool(requires_role=["marketing", "content"])
def write_blog_post():
    ...
```

### Audit Logging

```json
{
  "timestamp": "2025-11-21T07:45:00Z",
  "user": "mpaz",
  "tool": "generate_soap_notes",
  "params": {"prompt_type": "adult_neck_pain", "total": 10},
  "result": "success",
  "tokens_used": 25685,
  "cost": 0.95
}
```

---

## Scaling the Platform

### Adding a New Agent

1. **Create agent in claude-toolkit**:
   ```
   claude-toolkit/generated-agents/new-agent/
   ├── agent.py      # NewAgent class with execute() method
   ├── AGENT.json    # Metadata
   └── README.md     # Documentation
   ```

2. **Register in orchestrator config**:
   ```json
   // config/agents.json
   {
     "name": "new-agent",
     "description": "Does something useful",
     "path": ".../generated-agents/new-agent",
     "type": "python",
     ...
   }
   ```

3. **Create MCP tool module**:
   ```python
   # src/mcp/tools/new_domain/action.py
   def register_tools(mcp, config_loader, python_runner):
       @mcp.tool()
       def do_something(...):
           agent = config_loader.get_agent("new-agent")
           return python_runner.run_agent(agent, config)
   ```

4. **Register in server.py**:
   ```python
   from tools.new_domain import register_tools as register_new
   register_new(mcp, config_loader, python_runner)
   ```

5. **Done**: Tool immediately available to all clients.

### Adding a New Client

Any MCP-compatible client can connect:

| Client Type | Connection Method |
|-------------|------------------|
| Claude Code | `.mcp.json` in project |
| VS Code | Cursor/Continue extension |
| Web App | MCP client SDK (HTTP) |
| Slack Bot | MCP client SDK (HTTP) |
| Custom CLI | MCP client library |

No server changes required.

---

## Future Roadmap

### Phase 1: Foundation (Complete)
- [x] MCP server with FastMCP
- [x] Modular tool structure
- [x] synth-notes integration
- [x] Core orchestrator tools (list_agents, list_skills)

### Phase 2: GitHub Integration
- [ ] sync_github_repos tool
- [ ] collect_github_issues tool
- [ ] run_trend_analysis tool
- [ ] run_commit_analysis tool

### Phase 3: Research & Content
- [ ] research_topic tool
- [ ] analyze_competitors tool
- [ ] write_blog_post tool
- [ ] social media tools

### Phase 4: Enterprise Features
- [ ] Authentication/authorization
- [ ] Usage tracking dashboard
- [ ] Cost allocation
- [ ] Multi-tenant support

### Phase 5: Advanced Orchestration
- [ ] Agent pipelines (chain agents together)
- [ ] Scheduled agent execution
- [ ] Event-triggered agents
- [ ] Agent marketplace

---

## Conclusion

The Orchestrator MCP Server transforms fragmented tooling into a unified agent platform. By exposing all capabilities through MCP:

1. **Users** get natural language access to all tools
2. **Developers** write agents once, deploy everywhere
3. **Organizations** get centralized management and visibility
4. **Tools** become composable with Claude's native abilities

This is not just an improvement to workflow—it's a new paradigm for how humans and AI collaborate on complex tasks.

---

## Appendix: File Structure

```
orchestrator/
├── src/
│   ├── orchestrator/
│   │   ├── orchestrator.py          # Execution engine
│   │   ├── config.py                # Configuration management
│   │   ├── python_agent_runner.py   # Agent instantiation
│   │   └── agent_runner.py          # Claude Code agent runner
│   │
│   └── mcp/
│       ├── server.py                # MCP server entry point
│       └── tools/
│           ├── synth_notes/
│           │   └── generate.py
│           └── github_pm/           # (future)
│               ├── sync.py
│               └── collect.py
│
├── config/
│   ├── agents.json                  # Agent registry
│   ├── skills.json                  # Skill registry
│   └── repos.json                   # Repository registry
│
├── docs/
│   └── architecture/
│       └── MCP_SERVER_ARCHITECTURE.md  # This document
│
└── .mcp.json                        # MCP server config for Claude Code
```

---

*This document describes the architecture as of 2025-11-21. The platform is actively evolving.*
