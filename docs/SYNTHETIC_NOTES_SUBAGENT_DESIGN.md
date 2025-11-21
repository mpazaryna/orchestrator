# Synthetic Notes Subagent Design Analysis

**Date**: 2025-11-20
**Purpose**: Design a subagent for the orchestrator to leverage the synthetic-notes generation mechanism

## Current State Analysis

### Synthetic-Notes Architecture

The synthetic-notes system has a proven, elegant architecture:

**Core Components:**
1. **Two-Tier Prompt System**
   - Base system prompt (`adult_base_system.md` or `base_system.md`) - defines SOAP structure, coding standards
   - Condition-specific prompts (`adult_neck_pain.md`, etc.) - layer on specific clinical presentations
   - Combined via: `base_prompt + "\n\n---\n\n" + specific_prompt`

2. **Batch Generation Workflow**
   - Single API call generates multiple notes (configurable batch size)
   - Delimiter-based parsing (`---NEXT NOTE---`)
   - Cost tracking per batch with detailed usage statistics
   - Auto-numbered batch folders (`batch_001`, `batch_002`, etc.)

3. **Output Organization**
   ```
   output/
     batch_001/
       adult_neck_pain_a3f5d8e2.md
       adult_neck_pain_b4g6f9h3.md
     batch_002/
       adult_chronic_lbp_c5h7g0i4.md
   ```

4. **Quality Mechanisms**
   - Highly specific prompts with clinical constraints
   - Realistic brevity requirements ("Keep histories BRIEF and VAGUE")
   - Anatomical specificity requirements
   - Proper ICD-10/CPT coding validation
   - Evidence-based technique enforcement

5. **File Structure**
   ```
   src/
     main.py              # Core generation engine (300 lines)
     upload_notes.py      # Supabase integration
     clear_supabase.py    # Database cleanup
   prompts/
     base_system.md       # Pediatric SOAP structure
     adult_base_system.md # Adult SOAP structure
     adult_neck_pain.md   # Condition-specific guidance
     adult_chronic_lbp.md
     ...
   ```

**Key Design Principles:**
- **Simple over complex**: No complex dependencies, pure Python + Anthropic SDK
- **Batch processing**: Efficient token usage via multi-note generation
- **Cost transparency**: Detailed usage tracking and reporting
- **Deterministic output**: Auto-incrementing batch folders, consistent naming
- **Template-driven**: Prompts are markdown files, easy to modify
- **Quality over quantity**: Emphasis on clinical accuracy and realism

### Orchestrator Architecture

The orchestrator has a different, more flexible architecture:

**Core Components:**
1. **Configuration-Driven**
   - `config/repos.json` - Repository definitions
   - `config/skills.json` - Skill catalog (13 skills)
   - `config/agents.json` - Agent configurations

2. **Agent Execution Model**
   - `AgentRunner` class - Autonomous agent with tool use
   - Tool-based file operations (read, write, list, search)
   - Iterative execution loop (max 25 iterations)
   - System tracks files created/modified

3. **Interactive Selection**
   - `InteractiveMenu` class - Clean TUI for skill/repo selection
   - Multi-select capability
   - Skill discovery and filtering

4. **Multi-Repository Workflow**
   - Process multiple repos in parallel
   - Results saved to JSON
   - Per-repo success/failure tracking

**Key Design Principles:**
- **Multi-target execution**: Run same skill across many repos
- **Tool-based agents**: Autonomous exploration and file creation
- **Configuration as code**: JSON-based skill/repo definitions
- **Interactive workflows**: Menu-driven selection
- **Parallel processing**: Batch operations across repos

## The Design Challenge

**Core Question**: How should synthetic-notes generation fit into the orchestrator model?

### Option 1: Skill-Based Integration (Mismatched Model)

Make synthetic-notes a "skill" in the orchestrator:

```json
{
  "name": "soap-note-generator",
  "description": "Generate synthetic SOAP notes",
  "path": "/Users/mpaz/workspace/synthetic-notes",
  "mode": "agent",
  "tags": ["healthcare", "data-generation"],
  "output": "output/batch_XXX/"
}
```

**Problems with this approach:**
1. **Conceptual mismatch**: Skills analyze/document repositories. Synthetic-notes generates from prompts, not code.
2. **No repository input**: SOAP notes don't need repo context - they're generated from clinical prompts
3. **Batch semantics differ**: Orchestrator batches = "multiple repos", synthetic-notes batches = "multiple outputs"
4. **Agent tools unnecessary**: Don't need file exploration - just prompt → API → save
5. **Interactive menu misaligned**: Selecting repositories makes no sense for note generation

### Option 2: Standalone Script Mode (Status Quo)

Keep synthetic-notes completely separate:

```bash
# In synthetic-notes repo
uv run python src/main.py --prompt-type adult_neck_pain --total 10
```

**Advantages:**
- ✅ Clean separation of concerns
- ✅ No forced architecture mismatch
- ✅ Maintains simplicity of synthetic-notes
- ✅ Easy to use standalone

**Disadvantages:**
- ❌ No unified toolkit interface
- ❌ Manual navigation to synthetic-notes repo
- ❌ Can't leverage orchestrator's interactive menu
- ❌ Different UX paradigm

### Option 3: Generator-Specific Subagent Type (Recommended)

Create a new subagent category for "generators" that don't operate on repositories:

**Architecture:**

```json
// config/generators.json
{
  "generators": [
    {
      "name": "soap-notes",
      "description": "Generate synthetic clinical SOAP notes",
      "path": "/Users/mpaz/workspace/synthetic-notes",
      "type": "batch-generator",
      "prompt_types": [
        {
          "id": "adult_neck_pain",
          "label": "Adult - Neck Pain/Cervicalgia",
          "category": "adult"
        },
        {
          "id": "adult_chronic_lbp",
          "label": "Adult - Chronic Low Back Pain",
          "category": "adult"
        },
        {
          "id": "torticollis",
          "label": "Pediatric - Torticollis",
          "category": "pediatric"
        }
      ],
      "default_batch_size": 2,
      "default_total": 10,
      "output_base": "output",
      "supports_cost_tracking": true
    }
  ]
}
```

**New Orchestrator Components:**

1. **`GeneratorRunner` class** (parallel to `AgentRunner`):
   ```python
   class GeneratorRunner:
       """Runs batch generators that create synthetic data."""

       def run_generator(self, generator_config, options):
           """
           Execute generator with specified options.

           Args:
               generator_config: Generator metadata from config
               options: {
                   "prompt_type": "adult_neck_pain",
                   "total": 10,
                   "batch_size": 2,
                   "output_dir": None  # Use default
               }
           """
   ```

2. **Interactive Menu Extension**:
   ```
   Main Menu:
     1. Run Skill on Repositories (existing)
     2. Run Generator (NEW)
     3. List Skills
     4. List Generators (NEW)

   Generator Menu Flow:
     1. Select generator (soap-notes, future-generator, etc.)
     2. Select prompt type (adult_neck_pain, torticollis, etc.)
     3. Configure batch settings (total notes, batch size)
     4. Review and confirm
     5. Execute and show progress
   ```

3. **Generator Interface Abstraction**:
   ```python
   class GeneratorInterface:
       """Base class for generators."""

       def get_prompt_types(self) -> List[str]:
           """Return available prompt types."""

       def generate_batch(self, prompt_type: str, batch_size: int, options: dict):
           """Generate a batch of outputs."""

       def get_output_location(self) -> Path:
           """Return where outputs are saved."""
   ```

4. **Synthetic-Notes Adapter**:
   ```python
   class SyntheticNotesGenerator(GeneratorInterface):
       """Adapter for synthetic-notes generation system."""

       def __init__(self, repo_path: str):
           self.repo_path = Path(repo_path)
           self.prompts_dir = self.repo_path / "prompts"

       def generate_batch(self, prompt_type: str, batch_size: int, options: dict):
           """Call synthetic-notes main.py with appropriate args."""
           # Could either:
           # A) Import and call directly (if we add to orchestrator's deps)
           # B) Shell out via subprocess
           # C) Duplicate core logic (not DRY)
   ```

**Advantages:**
- ✅ Clean conceptual model: "Skills analyze repos, Generators create data"
- ✅ Leverages orchestrator's interactive menu UX
- ✅ Extensible to other generators (test data, mock APIs, etc.)
- ✅ Maintains synthetic-notes as source of truth
- ✅ Unified toolkit interface
- ✅ Can track usage stats across all generator runs

**Disadvantages:**
- ⚠️ Adds complexity to orchestrator
- ⚠️ Need to manage synthetic-notes as dependency or subprocess
- ⚠️ Two systems to maintain (orchestrator + synthetic-notes)

### Option 4: Hybrid - Global Launcher Script

Create a global launcher that bridges both systems:

```bash
#!/usr/bin/env bash
# /usr/local/bin/generate-notes

cd /Users/mpaz/workspace/synthetic-notes

# Interactive mode
if [ "$1" == "--interactive" ]; then
    # Show menu of prompt types
    echo "Select prompt type:"
    select prompt_type in adult_neck_pain adult_chronic_lbp torticollis; do
        read -p "Total notes: " total
        read -p "Batch size: " batch_size
        uv run python src/main.py --prompt-type "$prompt_type" --total "$total" --batch-size "$batch_size"
        break
    done
else
    # Pass through to main.py
    uv run python src/main.py "$@"
fi
```

**Advantages:**
- ✅ Minimal complexity
- ✅ Keeps systems independent
- ✅ Global access like orchestrator
- ✅ Can add basic interactivity

**Disadvantages:**
- ❌ Bash-based menu is crude compared to Python TUI
- ❌ Not unified with orchestrator
- ❌ Limited extensibility

## Recommendation: Option 3 with Phased Approach

### Phase 1: Global Launcher (Quick Win)
Create `/usr/local/bin/generate-notes` script for immediate utility.

### Phase 2: Generator Abstraction (Proper Architecture)
1. Add `config/generators.json` to orchestrator
2. Create `GeneratorRunner` class
3. Implement `GeneratorInterface` base class
4. Build `SyntheticNotesGenerator` adapter

### Phase 3: Interactive Integration
1. Extend `InteractiveMenu` with generator support
2. Add generator selection flow
3. Add configuration options (batch size, total, prompt type)

### Phase 4: Advanced Features
1. Cross-system usage tracking
2. Output management (view recent batches, search notes)
3. Prompt template editor
4. Quality validation and review workflows

## Critical Design Decisions

### 1. Dependency Management

**Question**: How should orchestrator interact with synthetic-notes?

**Options:**
- **A. Subprocess call**: Orchestrator shells out to `uv run python src/main.py`
  - Pro: Clean separation, no dependency hell
  - Con: Less control, harder to capture output

- **B. Import as library**: Add synthetic-notes to orchestrator's `pyproject.toml`
  - Pro: Direct function calls, better error handling
  - Con: Coupling, dependency conflicts

- **C. Shared library extraction**: Extract core generation logic to shared package
  - Pro: Clean architecture, reusable
  - Con: More complex, three repos to maintain

**Recommendation**: Start with **A (subprocess)**, evolve to **C** if we build more generators.

### 2. Configuration Location

**Question**: Where do generator configs live?

**Options:**
- **A. In orchestrator** (`config/generators.json`)
  - Pro: Centralized toolkit configuration
  - Con: Duplicates info from synthetic-notes

- **B. In synthetic-notes** (add `config.json`)
  - Pro: Single source of truth
  - Con: Orchestrator must read from multiple repos

- **C. Both with sync script**
  - Pro: Best of both worlds
  - Con: Complexity, sync issues

**Recommendation**: **A** - Orchestrator as the "toolkit index", synthetic-notes stays implementation.

### 3. Output Management

**Question**: Should orchestrator track generator outputs?

**Options:**
- **A. Track metadata only** (batch number, timestamp, count)
  - Pro: Lightweight
  - Con: Can't query/search notes

- **B. Full output tracking** (index all generated notes)
  - Pro: Rich queries, reporting
  - Con: Database needed, complexity

- **C. No tracking** (generator handles own outputs)
  - Pro: Simplest
  - Con: Disconnected from toolkit

**Recommendation**: Start with **C**, add **A** if usage patterns demand it.

## Implementation Sketch

### Minimal Generator Integration (1-2 hours of work)

**1. Add generator config**:
```json
// config/generators.json
{
  "generators": [
    {
      "name": "soap-notes",
      "description": "Generate synthetic clinical SOAP notes",
      "command": "cd /Users/mpaz/workspace/synthetic-notes && uv run python src/main.py",
      "prompt_types": ["adult_neck_pain", "adult_chronic_lbp", "torticollis"],
      "default_batch_size": 2
    }
  ]
}
```

**2. Add generator runner**:
```python
# src/orchestrator/generator_runner.py
import subprocess
from pathlib import Path

class GeneratorRunner:
    def run(self, generator_config, prompt_type, total, batch_size):
        cmd = [
            "bash", "-c",
            f"{generator_config['command']} --prompt-type {prompt_type} --total {total} --batch-size {batch_size}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result
```

**3. Add to orchestrator CLI**:
```python
# In orchestrator.py main()
parser.add_argument("--generate", action="store_true", help="Run generator mode")
parser.add_argument("--prompt-type", type=str, help="Generator prompt type")
parser.add_argument("--total", type=int, default=10, help="Total items to generate")
```

**Usage:**
```bash
uv run python orchestrator.py --generate --prompt-type adult_neck_pain --total 10
```

## Key Insights

1. **Don't force repository-centric model**: Generators are fundamentally different from repository analyzers

2. **Leverage what works**: Synthetic-notes has proven architecture - don't reinvent

3. **Think in categories**:
   - Skills = Analyze/document existing code
   - Generators = Create synthetic data from scratch
   - Agents = Autonomous task execution (future)

4. **Subprocess is underrated**: Clean separation beats tight coupling for cross-repo tools

5. **Interactive UX matters**: Orchestrator's menu system is valuable - extend it thoughtfully

6. **Start simple**: Global launcher script → Basic integration → Full generator framework

## Open Questions

1. **Should generators support multi-target?**
   - E.g., "Generate SOAP notes for 3 different conditions in parallel"
   - Probably not initially - batch generation already handles parallelism

2. **How to handle generator-specific config?**
   - Synthetic-notes has `.env` for API key
   - Should orchestrator set environment or pass through?

3. **Output directory conflicts?**
   - If running from orchestrator, where do batch folders go?
   - Respect synthetic-notes' default or allow orchestrator override?

4. **Cost tracking integration?**
   - Synthetic-notes tracks costs internally
   - Should orchestrator aggregate across all tool usage?
   - Probably yes - unified cost dashboard would be valuable

5. **Quality assurance?**
   - Should orchestrator add validation layer?
   - Or trust generator to handle quality?

## Next Steps

**If going with Phase 1 (Global Launcher):**
1. Write `/usr/local/bin/generate-notes` script
2. Test interactive prompt selection
3. Document usage in orchestrator README

**If going with Phase 2 (Generator Integration):**
1. Create `config/generators.json`
2. Implement `GeneratorRunner` class
3. Add `--generate` CLI flag
4. Test subprocess execution
5. Document generator pattern

**If ambitious (Full Integration):**
1. All of Phase 2, plus:
2. Extend `InteractiveMenu` with generator menu
3. Add prompt type selection UI
4. Implement batch configuration
5. Add progress reporting
6. Create generator documentation

## Conclusion

The synthetic-notes system is a **batch content generator**, not a **repository analyzer**. Forcing it into the "skill on repos" model would be architecturally wrong.

**Recommended path**:
1. Build generator abstraction in orchestrator
2. Use subprocess to call synthetic-notes
3. Extend interactive menu for generator workflow
4. Keep synthetic-notes as source of truth for SOAP note generation

This maintains clean separation while providing unified toolkit access.
