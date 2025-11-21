# Generate Synthetic SOAP Notes

Run the synth-notes-generator agent to create clinical training data.

## Instructions

Execute the following command to generate synthetic SOAP notes:

```bash
cd /Users/mpaz/workspace/orchestrator && uv run python orchestrator.py --run-agent synth-notes-generator --prompt-type {prompt_type} --total {total} --batch-size {batch_size}
```

## Configuration

Ask the user for (or use defaults):
- **prompt_type** (required): Which clinical scenario? Options:
  - Adult: `adult_neck_pain`, `adult_chronic_lbp`, `adult_trauma`, `adult_sports_injury`
  - Pediatric: `torticollis`, `plagiocephaly`, `feeding`, `wellness`
- **total** (default: 10): How many notes to generate
- **batch_size** (default: 2): Notes per API call

## Example

If user says "generate 5 neck pain notes":
```bash
cd /Users/mpaz/workspace/orchestrator && uv run python orchestrator.py --run-agent synth-notes-generator --prompt-type adult_neck_pain --total 5 --batch-size 2
```

## Output

Notes are saved to: `/Users/mpaz/workspace/synthetic-notes/output/batch_XXX/`

Report the results including:
- Batch folder created
- Number of notes generated
- Total cost
