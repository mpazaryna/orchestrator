# SOAP Notes Generator - Skill Design for Orchestrator

**Date**: 2025-11-20
**Corrected Understanding**: Skills are agent prompts that Claude Code executes with tool access

## The Real Architecture

### How Skills Actually Work

A "skill" is NOT code to execute - it's **instructions for Claude Code to follow as an autonomous agent**.

**Flow:**
1. User selects skill from orchestrator menu
2. Orchestrator loads `SKILL.md` from skill directory
3. Orchestrator calls Claude API with:
   - System prompt = SKILL.md content
   - Tools = [read_file, write_file, list_files, search_files, run_bash]
   - Initial message = "Execute this skill on repo X"
4. Claude Code runs agentic loop:
   - Reads files to understand context
   - Makes decisions based on skill instructions
   - Writes outputs
   - Continues until task complete
5. Orchestrator tracks iterations, files created, tool uses

**Example - Journal Skill:**
```markdown
# Git Journal

Generate a journal entry from your git history.

## Workflow
1. Read Git Log - Analyze recent commits
2. Generate Entry - Write journal from commit history
3. Save - Write to `docs/journal/YYYY-MM-DD-HHMM-slug.md`
```

Claude Code reads this, then autonomously:
- Runs `git log` via run_bash tool
- Analyzes commits
- Writes journal entry via write_file tool
- Stops when done

## SOAP Notes Generator Skill

### The Right Approach

Create a skill that instructs Claude Code to:
1. Read prompt templates from synthetic-notes repo
2. Call Anthropic API to generate SOAP notes
3. Save outputs to batch folders
4. Track costs and usage

**NOT subprocess to synthetic-notes** - Claude Code directly performs the generation.

### Draft SKILL.md

```markdown
---
name: soap-notes-generator
description: Generate synthetic clinical SOAP notes using prompt templates and batch processing
---

# Synthetic SOAP Notes Generator

Generate realistic chiropractic SOAP notes for clinical training datasets.

## Context

You will generate synthetic clinical documentation by:
1. Reading prompt templates from the synthetic-notes repository
2. Combining base system prompts with condition-specific prompts
3. Calling the Anthropic API to generate batches of notes
4. Saving outputs to organized batch folders
5. Tracking token usage and costs

## Prompt Architecture

The synthetic-notes system uses a two-tier prompt approach:

**Base Prompts** (define SOAP structure):
- `prompts/adult_base_system.md` - Adult patient documentation standards
- `prompts/base_system.md` - Pediatric patient documentation standards

**Condition Prompts** (specific clinical scenarios):
- `prompts/adult_neck_pain.md`
- `prompts/adult_chronic_lbp.md`
- `prompts/adult_trauma.md`
- `prompts/torticollis.md`
- `prompts/plagiocephaly.md`
- etc.

**Combination**: `base_prompt + "\n\n---\n\n" + condition_prompt`

## User Input Expected

The user will specify:
- **Prompt type**: Which condition to generate (e.g., "adult_neck_pain")
- **Total notes**: How many notes to create (default: 10)
- **Batch size**: Notes per API call (default: 2)

## Workflow

### 1. Determine Prompt Type

Ask user or use from orchestrator selection:
- Prompt type (e.g., "adult_neck_pain")
- Total notes to generate
- Batch size

### 2. Read Prompt Files

Use `read_file` tool to load:
- Base system prompt (adult_base_system.md or base_system.md)
- Condition-specific prompt (e.g., adult_neck_pain.md)

Combine them: `base + "\n\n---\n\n" + condition`

### 3. Determine Output Location

Find next available batch folder:
- Check `/Users/mpaz/workspace/synthetic-notes/output/`
- Find highest batch number (batch_001, batch_002, etc.)
- Create next batch folder (e.g., batch_006)

### 4. Generate Notes in Batches

For each batch:

**API Call Structure:**
```
Model: claude-opus-4-1-20250805
Max tokens: 8000
System prompt: <combined prompt from step 2>
User message: "Generate {batch_size} synthetic {adult|pediatric} chiropractic
              SOAP notes based on the focus areas described above.

              Separate each note with ---NEXT NOTE--- delimiter.
              Output ONLY the notes, nothing else."
```

**Parse Response:**
- Split on `---NEXT NOTE---` delimiter
- Each segment = one SOAP note
- Generate UUID for each note (use first 8 chars for filename)

**Track Usage:**
- Capture `usage.input_tokens` and `usage.output_tokens` from response
- Calculate costs:
  - Input: $15.00 per million tokens
  - Output: $75.00 per million tokens

### 5. Save Notes

For each note in batch:

**File structure:**
```
output/batch_XXX/{prompt_type}_{short_uuid}.md
```

**File content:**
```markdown
# SOAP Note

**ID:** {full-uuid}
**Prompt Type:** {prompt_type}
**Batch:** batch_{number}
**Generated:** {timestamp}

---

{note_content}
```

### 6. Report Results

After all batches complete, report:
- Total notes generated
- Batch folder location
- Token usage statistics:
  - Total input tokens
  - Total output tokens
  - Input cost
  - Output cost
  - Total cost

## Important Constraints

### API Key
- Read from environment variable: `ANTHROPIC_API_KEY`
- Use the same client instance for all calls

### Clinical Accuracy
The prompts enforce:
- Anatomically specific findings
- Proper ICD-10 and CPT coding
- Age-appropriate techniques
- Clinical rationale for treatments

### Pricing (Claude Opus 4)
- Input: $15.00 per million tokens
- Output: $75.00 per million tokens

### Batch Numbering
- Auto-increment from existing batches
- Format: `batch_001`, `batch_002`, etc. (zero-padded 3 digits)

### Delimiter
- Must use exactly `---NEXT NOTE---` for parsing
- Case-sensitive, exact match required

## Tool Usage

Use these tools to accomplish the task:

**read_file**: Load prompt templates from synthetic-notes repo
**write_file**: Save generated SOAP notes to batch folder
**list_files**: Find existing batch folders to determine next number
**run_bash**: Optional - check git status, create directories

## Example Execution

User request: "Generate 6 adult neck pain notes"

Your execution:
1. Read `prompts/adult_base_system.md`
2. Read `prompts/adult_neck_pain.md`
3. Combine prompts
4. Check output directory → finds batch_005 exists
5. Create batch_006 folder
6. Generate 3 batches of 2 notes each:
   - Batch 1: Call API, get 2 notes, save as adult_neck_pain_{uuid1}.md, adult_neck_pain_{uuid2}.md
   - Batch 2: Call API, get 2 notes, save files
   - Batch 3: Call API, get 2 notes, save files
7. Report: "Generated 6 notes in batch_006, cost: $0.45"

## Error Handling

- If ANTHROPIC_API_KEY not found → stop and report error
- If prompt file missing → stop and report which file
- If API call fails → report error and stop (don't continue with partial batches)
- If batch folder creation fails → report error

## Success Criteria

Task is complete when:
- All requested notes are generated
- Files saved to batch folder
- Usage statistics reported
- No errors occurred

Stop when done. Do not ask for confirmation.
```

## Key Insights I Missed

1. **Skills are prompts, not code**: The SKILL.md IS the agent's instructions
2. **Claude Code is the executor**: No need for subprocess - Claude has full tool access
3. **Direct API access**: Claude Code can call Anthropic API directly (has access to client via environment)
4. **Autonomous completion**: Agent decides when task is done based on skill instructions

## What This Enables

With this skill in the orchestrator:

**User workflow:**
```bash
uv run python orchestrator.py --interactive
# → Select skill: "soap-notes-generator"
# → Configure: prompt_type=adult_neck_pain, total=10, batch_size=2
# → Claude Code autonomously generates notes
# → Reports completion with costs
```

**Or via direct args:**
```bash
uv run python orchestrator.py --skill soap-notes-generator \
  --prompt-type adult_neck_pain --total 10 --batch-size 2
```

## Implementation Path

### 1. Create Skill Directory
```
/Users/mpaz/workspace/claude-toolkit/generated-skills/soap-notes-generator/
├── SKILL.md (the prompt above)
├── README.md (documentation)
└── template.md (optional - example output structure)
```

### 2. Add to skills.json
```json
{
  "name": "soap-notes-generator",
  "description": "Generate synthetic clinical SOAP notes using AI",
  "path": "/Users/mpaz/workspace/claude-toolkit/generated-skills/soap-notes-generator",
  "mode": "agent",
  "tags": ["healthcare", "data-generation", "synthetic-data"],
  "repo_types": ["healthcare"],
  "version": "1.0.0",
  "output": "Batch folder with generated SOAP notes"
}
```

### 3. Handle User Input

The orchestrator needs to pass parameters to the skill. Options:

**A. Extend interactive menu** to collect:
- Prompt type selection
- Total notes (numeric input)
- Batch size (numeric input)

**B. Pass via initial context:**
```python
# In orchestrator.py
initial_message = f"""Please execute the 'soap-notes-generator' skill.

Configuration:
- Prompt type: {args.prompt_type}
- Total notes: {args.total}
- Batch size: {args.batch_size}
- Output base: /Users/mpaz/workspace/synthetic-notes/output/

Use the available tools to complete the task."""
```

### 4. Agent Execution

Claude Code will:
1. Read SKILL.md to understand task
2. Parse configuration from initial message
3. Use `read_file` to load prompts from synthetic-notes repo
4. Make API calls to generate notes (has access to Anthropic client)
5. Use `write_file` to save notes to batch folders
6. Report completion with statistics

## Open Questions

### How does Claude Code access Anthropic API?

**Need to verify**: Can Claude Code running as an agent make Anthropic API calls?

**Options:**
1. **Direct access**: If orchestrator provides client instance in context
2. **Tool wrapper**: Add `call_anthropic_api` to tool definitions
3. **Python execution**: Add `run_python` tool that executes Python code with imports

**Most likely need**: Add a tool for API calls:

```python
# In agent_tools.py
def _call_anthropic_api(self, tool_input):
    """Make an Anthropic API call."""
    from anthropic import Anthropic
    import os

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model=tool_input["model"],
        max_tokens=tool_input["max_tokens"],
        system=tool_input.get("system"),
        messages=tool_input["messages"]
    )

    return {
        "content": response.content[0].text,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    }
```

Then add to tool definitions:
```python
{
    "name": "call_anthropic_api",
    "description": "Call Anthropic API to generate content",
    "input_schema": {...}
}
```

## Comparison to Original synthetic-notes

**Original approach:**
- Standalone Python script
- Direct API calls
- Batch logic in Python code
- Cost tracking in Python

**Agent-based approach:**
- Claude Code as executor
- Skill as instructions
- Logic executed by LLM (Claude Code)
- Still uses Anthropic API, but called by agent

**Advantages of agent approach:**
- Unified toolkit interface
- Interactive selection
- Can adapt to errors/changes
- Natural language configuration

**Disadvantages:**
- More complex execution path
- Requires tool for API access
- Potential for agent confusion
- Less deterministic than Python code

## Recommendation

**Implement both approaches:**

1. **Keep synthetic-notes standalone** - It works well, proven architecture
2. **Add soap-notes-generator skill** - Provides unified interface via orchestrator
3. **Skill calls synthetic-notes** - Use `run_bash` tool to execute the Python script:

```markdown
## Execution Method

Use the `run_bash` tool to call the synthetic-notes generator:

```bash
cd /Users/mpaz/workspace/synthetic-notes && \
  uv run python src/main.py \
    --prompt-type {prompt_type} \
    --total {total} \
    --batch-size {batch_size}
```

Parse the output to extract:
- Batch folder location
- Token usage stats
- Cost information

Report these back to the user.
```

**This approach:**
- Leverages existing proven code ✅
- Provides orchestrator integration ✅
- Minimal complexity ✅
- Claude Code just orchestrates, doesn't reimplement ✅

## Revised Implementation

**Simpler SKILL.md:**
```markdown
# Synthetic SOAP Notes Generator

Execute the synthetic-notes generator to create clinical training data.

## Workflow

1. **Get configuration** from user:
   - Prompt type (adult_neck_pain, adult_chronic_lbp, torticollis, etc.)
   - Total notes (default: 10)
   - Batch size (default: 2)

2. **Execute generator**:
   ```bash
   cd /Users/mpaz/workspace/synthetic-notes && \
     uv run python src/main.py \
       --prompt-type {prompt_type} \
       --total {total} \
       --batch-size {batch_size}
   ```

3. **Parse output** from stderr:
   - Batch folder location
   - Token usage (input/output)
   - Cost statistics

4. **Report results**:
   - Batch folder path
   - Notes generated
   - Total cost

Use `run_bash` tool to execute the command.
```

**This is the right level of abstraction** - Let synthetic-notes do what it does well, use the orchestrator for integration and UX.
