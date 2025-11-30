# Using Synth-Notes Skill with Orchestrator

**Created**: 2025-11-20
**Skill**: synth-notes (v1.0.0)

## Overview

The `synth-notes` skill integrates the synthetic-notes SOAP note generator into the orchestrator toolkit. This allows you to generate clinical training data through the orchestrator's unified interface.

## What It Does

The skill orchestrates the synthetic-notes generator to create batches of realistic chiropractic SOAP notes with:
- Anatomically specific findings
- Proper ICD-10 and CPT coding
- Age-appropriate clinical techniques
- Realistic patient presentations
- Full cost and token usage tracking

## Quick Start

### Option 1: Interactive Mode

```bash
cd /Users/mpaz/workspace/orchestrator
uv run python orchestrator.py --interactive
```

Then:
1. Select skill: **synth-notes**
2. Select repository: **synthetic-notes**
3. The agent will ask you to specify:
   - Prompt type (e.g., adult_neck_pain)
   - Total notes to generate
   - Batch size

### Option 2: Direct Execution

From the orchestrator directory, you can also navigate and run via tmux:

```bash
# Start tmux session
./tmux_interactive.sh

# In window 1 or 2:
uv run python orchestrator.py --interactive
# Select synth-notes skill
```

## Available Prompt Types

### Adult Cases (Ages 18-65+)
- `adult_trauma` - Acute trauma, MVA, falls, work injuries
- `adult_chronic_lbp` - Chronic low back pain, degenerative conditions
- `adult_neck_pain` - Cervicalgia, tech neck, postural strain
- `adult_sports_injury` - Sports injuries, athletic performance

### Pediatric Cases (Infants)
- `torticollis` - Infant torticollis (congenital, positional)
- `plagiocephaly` - Cranial asymmetry
- `feeding` - Feeding difficulties
- `wellness` - General wellness exams

## Example Workflow

**Task**: Generate 10 adult neck pain cases

**Via Interactive Menu**:
1. Run: `uv run python orchestrator.py --interactive`
2. Select skill: `synth-notes`
3. Select repo: `synthetic-notes`
4. Agent starts and prompts for configuration
5. Specify: `prompt_type: adult_neck_pain, total: 10, batch_size: 2`
6. Agent executes generator
7. Reports results with cost breakdown

**Expected Output**:
```
✅ SOAP Notes Generation Complete

Batch folder: batch_006
Location: /Users/mpaz/workspace/synthetic-notes/output/batch_006/
Notes generated: 10
Prompt type: adult_neck_pain

Token Usage:
  Input tokens:  16,225
  Output tokens: 9,460
  Total tokens:  25,685

Cost:
  Input cost:  $0.24
  Output cost: $0.71
  Total cost:  $0.95

Files created:
  adult_neck_pain_a3f5d8e2.md
  adult_neck_pain_b4g6f9h3.md
  ...
```

## Output Location

All generated notes are saved to:
```
/Users/mpaz/workspace/synthetic-notes/output/batch_XXX/
```

Batch folders are auto-numbered: `batch_001`, `batch_002`, etc.

Each note file includes:
- Unique ID (UUID)
- Metadata (prompt type, batch, timestamp)
- Complete SOAP note (Subjective, Objective, Assessment, Plan, Billing)

## Cost Estimates

Based on Claude Opus 4 pricing ($15 input / $75 output per million tokens):

| Notes | Typical Cost |
|-------|--------------|
| 10    | $0.50 - $2.00 |
| 25    | $1.25 - $5.00 |
| 50    | $2.50 - $10.00 |

Costs vary based on:
- Complexity of prompt type
- Batch size (smaller batches = more overhead)
- Note detail and length

## Requirements

1. **synthetic-notes repository** must be at: `/Users/mpaz/workspace/synthetic-notes`
2. **ANTHROPIC_API_KEY** must be set in synthetic-notes `.env` file
3. **uv package manager** must be installed

## How It Works

The skill is an **orchestrator wrapper pattern**:

```
User → Orchestrator (interactive)
     → synth-notes skill (SKILL.md)
     → Claude Code agent (autonomous)
     → run_bash tool (execute Python)
     → synthetic-notes generator (proven logic)
     → Parse output & report
```

The agent:
1. Reads skill instructions from SKILL.md
2. Validates user configuration
3. Executes synthetic-notes via `run_bash` tool
4. Parses stderr output for statistics
5. Verifies files were created
6. Reports comprehensive results

This approach:
- ✅ Leverages proven generation code
- ✅ Provides unified toolkit interface
- ✅ Maintains clean separation
- ✅ Enables interactive configuration

## Troubleshooting

### Error: ANTHROPIC_API_KEY not set

**Solution**: Configure the API key in synthetic-notes:
```bash
cd /Users/mpaz/workspace/synthetic-notes
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```

### Error: synthetic-notes not found

**Solution**: Verify the path in `config/repos.json` points to correct location.

### Error: Invalid prompt type

**Solution**: Use one of the valid prompt types listed above.

### Error: Rate limit exceeded

**Solution**:
- Check Anthropic API quota/credits
- Reduce batch size (try `--batch-size 1`)
- Wait a few minutes and retry

## Advanced Usage

### Generate Multiple Batches

Run the skill multiple times with different prompt types:

1. Run synth-notes with `adult_neck_pain`
2. Run synth-notes with `adult_chronic_lbp`
3. Run synth-notes with `torticollis`

Each execution creates a new batch folder.

### Custom Batch Sizes

For better quality with longer notes, use smaller batch sizes:
- Default: 2 notes per batch
- For complex cases: 1 note per batch
- For simple cases: up to 5 notes per batch

### Group Operations

Since synthetic-notes is tagged with `healthcare`, you can run other skills on it:

```bash
# Document the synthetic-notes codebase
uv run python orchestrator.py --skill repo-summarizer --repo-names synthetic-notes

# Create journal of synthetic-notes development
uv run python orchestrator.py --skill journal --repo-names synthetic-notes
```

## File Structure

```
orchestrator/
├── config/
│   ├── repos.json (includes synthetic-notes)
│   └── skills.json (includes synth-notes skill)
└── docs/
    └── SYNTH_NOTES_USAGE.md (this file)

claude-toolkit/
└── generated-skills/
    └── synth-notes/
        ├── SKILL.md (agent instructions)
        ├── README.md (documentation)
        └── template.md (example outputs)

synthetic-notes/
├── src/
│   └── main.py (generation engine)
├── prompts/
│   ├── adult_base_system.md
│   ├── adult_neck_pain.md
│   └── ...
└── output/
    ├── batch_001/
    ├── batch_002/
    └── ...
```

## Next Steps

1. Try generating a small batch (5-10 notes) to test
2. Review generated notes for quality
3. Adjust batch size based on needs
4. Scale up to larger batches once validated

## Notes

- The skill does NOT modify synthetic-notes code - it calls it as-is
- Output files stay in synthetic-notes/output directory
- Batch numbering is automatic and sequential
- Each execution is fully tracked with costs
