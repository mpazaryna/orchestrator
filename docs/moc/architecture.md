---
title: Orchestrator Architecture Guide
type: moc
generated: 2025-11-20
last_updated: 2025-11-20
project: orchestrator
---

# Architecture Guide

This document details the system architecture, design decisions, and technical implementation of the Generic Orchestrator for Claude Skills.

## System Overview

The orchestrator is built as a **flexible automation pipeline** that bridges human-defined skills with AI execution capabilities across multiple repositories.

### High-Level Architecture

```mermaid
graph TB
    subgraph "User Interface"
        A[CLI Arguments] --> B[Argument Parser]
        B --> C[Configuration Loader]
    end
    
    subgraph "Skill Management"  
        D[Skill Discovery] --> E[Skill Loader]
        E --> F[Template Resolution]
        F --> G[Metadata Extraction]
    end
    
    subgraph "Repository Processing"
        H[Repository Scanner] --> I[Context Collector]
        I --> J[File Structure Analysis]
        I --> K[Manifest Detection]
    end
    
    subgraph "Execution Engine"
        L[Simple Mode] --> M[Single API Call]
        N[Agent Mode] --> O[Tool-Enabled Agent]
        O --> P[Multi-Turn Conversation]
    end
    
    subgraph "Output Management"
        Q[Output Writer] --> R[Repository Files]
        Q --> S[Summary JSON]
    end
    
    C --> D
    C --> H
    G --> L
    G --> N
    J --> L
    J --> N
    K --> L
    K --> N
    M --> Q
    P --> Q
```

## Core Design Principles

### 1. Skill-Agnostic Execution

The orchestrator doesn't hardcode specific skills but dynamically loads them from a standardized format:

```mermaid
flowchart LR
    A[SKILL.md Files] --> B[Skill Loader]
    B --> C[Dynamic Execution]
    
    subgraph "Skill Structure"
        D[SKILL.md]
        E[template.md optional]
        F[Metadata Extraction]
    end
    
    B --> D
    B --> E  
    B --> F
```

**Benefits**:
- **Extensibility**: New skills require no code changes
- **Maintainability**: Skill logic separated from execution logic
- **Flexibility**: Skills can define their own output patterns and requirements

### 2. Context-Rich Repository Analysis

The system prioritizes providing comprehensive context to AI models for better results:

```mermaid
graph TB
    A[Repository] --> B[File Discovery]
    B --> C[Content Filtering]
    C --> D[Structure Analysis]
    
    A --> E[Manifest Detection]
    E --> F[Package Information]
    
    A --> G[Documentation Scan]
    G --> H[README Extraction]
    
    D --> I[Context Bundle]
    F --> I
    H --> I
    
    I --> J[AI Analysis]
```

**Context Collection Strategy**:
- **Breadth**: File structure overview (up to 100 files)
- **Depth**: Important file content (README, manifests)
- **Filtering**: Exclusion of build artifacts and dependencies
- **Relevance**: Technology stack detection

### 3. Dual Execution Architecture

The orchestrator supports two execution modes for different use cases:

```mermaid
sequenceDiagram
    participant User
    participant Orchestrator
    participant Claude API
    participant Repository
    
    Note over User, Repository: Simple Mode
    User->>Orchestrator: Run skill (--simple)
    Orchestrator->>Claude API: Single prompt + context
    Claude API->>Orchestrator: Generated output
    Orchestrator->>Repository: Write output file
    
    Note over User, Repository: Agent Mode (Default)
    User->>Orchestrator: Run skill (--agent)
    loop Multi-turn conversation
        Orchestrator->>Claude API: Request with tools
        Claude API->>Orchestrator: Tool usage + response
        Orchestrator->>Repository: Execute tool operations
    end
    Orchestrator->>Repository: Final output files
```

## Component Architecture

### Core Orchestrator (`orchestrator.py`)

**Responsibilities**:
- CLI interface and argument parsing
- Configuration management
- Skill discovery and loading
- Repository batch processing
- Output coordination

```mermaid
classDiagram
    class Orchestrator {
        +main() CLI entry point
        +load_skill(name) Dynamic skill loading
        +collect_repo_context(path) Context extraction
        +process_repo_with_skill() Single repo processing
        +list_available_skills() Skill discovery
        -extract_skill_metadata() Metadata parsing
    }
    
    class SkillLoader {
        +definition: str
        +template: str
        +metadata: dict
    }
    
    class ContextCollector {
        +file_structure: list
        +manifests: dict
        +readme_content: str
    }
    
    Orchestrator --> SkillLoader : loads
    Orchestrator --> ContextCollector : uses
```

**Key Design Decisions**:

1. **Single File Design**: Everything in one file for simplicity and deployment
2. **Function-Based**: No complex OOP hierarchy, clear data flow
3. **Error Isolation**: Repository failures don't stop batch processing
4. **Configurable Paths**: Both defaults and runtime overrides

### Agent Runner (`agent_runner.py`)

**Responsibilities**:
- Multi-turn conversation management
- Tool execution coordination
- Agent state tracking
- Resource limit enforcement

```mermaid
stateDiagram-v2
    [*] --> Initialize
    Initialize --> BuildPrompt
    BuildPrompt --> CallClaude
    
    CallClaude --> CheckResponse
    CheckResponse --> ToolUse : Has tool use
    CheckResponse --> Complete : No tool use / end_turn
    
    ToolUse --> ExecuteTools
    ExecuteTools --> SendResults
    SendResults --> CallClaude
    
    Complete --> [*]
    
    note right of CallClaude : Max 25 iterations
    note right of ExecuteTools : File operations tracked
```

**Agent Features**:
- **Iteration Limiting**: Prevents infinite loops (max 25 turns)
- **Tool Tracking**: Complete log of all tool executions
- **File Monitoring**: Tracks created and modified files
- **Conversation History**: Full message thread preservation

### Tool System (`agent_tools.py`)

**Tool Architecture**:

```mermaid
graph LR
    A[Agent Request] --> B[Tool Executor]
    
    B --> C[read_file]
    B --> D[write_file]
    B --> E[list_files]
    B --> F[search_files]
    B --> G[run_bash]
    
    C --> H[Repository Files]
    D --> H
    E --> H
    F --> H
    G --> I[Shell Commands]
```

**Tool Design Principles**:
1. **Safety**: All operations scoped to repository directory
2. **Timeouts**: 30-second limit on all operations
3. **Error Handling**: Graceful failure with detailed error messages
4. **Logging**: Complete operation tracking for debugging

**Tool Implementation Example**:
```python
def _write_file(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    file_path = self.repo_path / tool_input["path"]
    
    # Create parent directories if needed
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(tool_input["content"])
        return {"success": True, "path": str(file_path)}
    except Exception as e:
        return {"error": f"Failed to write file: {str(e)}"}
```

## Data Flow Architecture

### Repository Processing Pipeline

```mermaid
flowchart TD
    A[Repository List] --> B[For Each Repository]
    B --> C[Validate Path]
    C --> D[Collect Context]
    
    D --> E[File Structure Scan]
    D --> F[Manifest Discovery]
    D --> G[README Extraction]
    
    E --> H[Context Bundle]
    F --> H
    G --> H
    
    H --> I{Execution Mode}
    I -->|Simple| J[Single API Call]
    I -->|Agent| K[Agent Execution]
    
    J --> L[Process Response]
    K --> M[Multi-Turn Processing]
    
    L --> N[Write Output]
    M --> N
    
    N --> O[Track Results]
    O --> P[Next Repository]
    P --> B
    
    O --> Q[Generate Summary]
```

### Context Collection Strategy

```mermaid
graph TB
    subgraph "File Discovery"
        A[find command] --> B[Filter Exclusions]
        B --> C[Limit to 100 files]
    end
    
    subgraph "Manifest Detection"
        D[pyproject.toml] --> E[Technology Stack]
        F[package.json] --> E
        G[requirements.txt] --> E
        H[Cargo.toml] --> E
        I[go.mod] --> E
        J[pom.xml] --> E
        K[build.gradle] --> E
    end
    
    subgraph "Content Extraction"
        L[README.md] --> M[Project Description]
        N[Documentation Files] --> M
    end
    
    C --> O[Repository Context]
    E --> O
    M --> O
    
    O --> P[AI Analysis]
```

**Filtering Logic**:
```bash
# Automated exclusions
*/.*           # Hidden files and directories
*/node_modules/*   # Node.js dependencies
*/__pycache__/*    # Python cache
*/venv/*       # Virtual environments
*/.venv/*      # UV virtual environments
```

## Skill Integration Architecture

### Skill Loading Mechanism

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant FS as File System
    participant SL as Skill Loader
    participant SM as Skill Metadata
    
    O->>FS: List toolkit directory
    FS->>O: Available skill directories
    
    loop For each skill
        O->>SL: Load skill definition
        SL->>FS: Read SKILL.md
        FS->>SL: Skill content
        SL->>FS: Check for template.md
        FS->>SL: Template content (optional)
        SL->>SM: Extract metadata
        SM->>SL: Parsed metadata
        SL->>O: Complete skill object
    end
```

### Metadata Extraction System

The orchestrator analyzes skill definitions to determine output patterns:

```python
def extract_skill_metadata(skill_definition: str) -> dict:
    metadata = {
        "output_location": None,
        "output_filename": None, 
        "creates_directory": False
    }
    
    # Pattern matching for common outputs
    if "docs/moc/" in skill_definition.lower():
        metadata["output_location"] = "docs/moc"
        metadata["creates_directory"] = True
    
    if "project.md" in skill_definition.lower():
        metadata["output_filename"] = "PROJECT.md"
        
    return metadata
```

## API Integration Architecture

### Claude API Client Design

```mermaid
graph LR
    A[Orchestrator] --> B[API Client Config]
    B --> C[Claude Sonnet 4]
    
    subgraph "Request Processing"
        D[System Prompt] --> E[User Message]
        E --> F[Tool Definitions]
        F --> G[API Request]
    end
    
    subgraph "Response Handling"  
        H[Response Content] --> I[Tool Use Detection]
        I --> J[Content Extraction]
        J --> K[Error Handling]
    end
    
    C --> D
    G --> C
    C --> H
```

**API Configuration**:
- **Model**: `claude-sonnet-4-20250514`
- **Max Tokens**: 8000 (for comprehensive output)
- **Tool Support**: Full tool use capability in agent mode
- **System Prompts**: Skill-specific instructions

**Error Handling Strategy**:
- Network timeouts with retry logic
- Rate limiting awareness
- Token limit management
- Response validation

## Security Architecture

### File System Security

```mermaid
graph TB
    A[User Input] --> B[Path Validation]
    B --> C[Repository Boundary Check]
    C --> D[Permission Verification]
    
    E[Tool Operations] --> F[Scoped File Access]
    F --> G[Timeout Enforcement]
    G --> H[Error Containment]
    
    I[API Keys] --> J[Environment Variables]
    J --> K[.env File Security]
    
    subgraph "Security Measures"
        L[Path Normalization]
        M[Directory Traversal Prevention]
        N[Command Injection Prevention]
        O[Timeout Limits]
    end
    
    B --> L
    C --> M
    G --> N
    G --> O
```

### Security Implementation

**Path Sanitization**:
```python
def validate_repo_path(path: str) -> Path:
    """Validate and sanitize repository paths."""
    normalized = Path(path).resolve()
    
    # Prevent directory traversal
    if ".." in str(normalized):
        raise ValueError("Invalid path: directory traversal detected")
    
    return normalized
```

**Command Execution Safety**:
```python
def _run_bash(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """Execute bash commands with safety constraints."""
    command = tool_input["command"]
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=self.repo_path,  # Scoped to repository
            capture_output=True,
            text=True,
            timeout=30  # Hard timeout limit
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr, 
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out after 30 seconds"}
```

## Performance Architecture

### Resource Management

```mermaid
graph TB
    subgraph "Memory Management"
        A[Context Limiting] --> B[100 File Limit]
        C[Content Truncation] --> D[5000 char limit per file]
    end
    
    subgraph "Time Management"
        E[API Timeouts] --> F[8000 token responses]
        G[Tool Timeouts] --> H[30 second limits]
        I[Agent Limits] --> J[25 iteration max]
    end
    
    subgraph "Concurrency Control"
        K[Sequential Processing] --> L[Error Isolation]
        M[Future: Parallel] --> N[Rate Limiting]
    end
```

### Scalability Considerations

**Current Limitations**:
- Sequential repository processing
- No caching of analysis results
- Fixed resource limits (100 files, 5000 chars)

**Future Optimizations**:
- Parallel processing with rate limiting
- Git-hash based caching
- Dynamic resource allocation
- Incremental analysis

## Deployment Architecture

### Development Setup

```mermaid
graph LR
    A[uv sync] --> B[Virtual Environment]
    B --> C[Dependencies Installed]
    C --> D[.env Configuration]
    D --> E[API Key Setup]
    E --> F[Ready to Run]
    
    subgraph "Dependencies"
        G[anthropic>=0.40.0]
        H[python-dotenv>=1.0.0]
    end
    
    C --> G
    C --> H
```

### Configuration Management

**Environment Variables**:
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-api03-...

# Optional Configuration
SKILLS_BASE_PATH=/path/to/claude-toolkit/generated-skills
```

**Runtime Configuration**:
```python
DEFAULT_REPOS = [
    "/Users/mpaz/workspace/mcp-fleet",
    "/Users/mpaz/workspace/rishi",
]
```

## Monitoring and Observability

### Execution Tracking

```mermaid
graph TB
    A[Orchestrator Start] --> B[Repository Processing]
    B --> C[Status Tracking]
    
    C --> D[Success Metrics]
    C --> E[Error Logging]  
    C --> F[Performance Data]
    
    D --> G[Files Created Count]
    D --> H[Processing Time]
    D --> I[Tool Usage Stats]
    
    E --> J[Error Messages]
    E --> K[Failed Operations]
    E --> L[Recovery Actions]
    
    F --> M[Iteration Counts]
    F --> N[API Call Metrics]
    F --> O[Resource Usage]
    
    G --> P[Summary JSON]
    J --> P
    M --> P
```

### Result Persistence

**Summary JSON Format**:
```json
{
  "repo": "project-name",
  "path": "/full/path/to/repo",
  "skill": "project-moc-generator", 
  "status": "success|error",
  "mode": "agent|simple",
  "iterations": 12,
  "files_created": ["docs/moc/README.md"],
  "files_modified": ["docs/moc/README.md"],
  "tool_uses_count": 23,
  "timestamp": "2025-11-20T10:30:00"
}
```

This architecture provides a solid foundation for AI-powered repository automation while maintaining flexibility for future enhancements and scaling requirements.