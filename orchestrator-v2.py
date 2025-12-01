#!/usr/bin/env python3
"""
Simple autonomous agent runner - proof of concept.
Runs the reporter agent against a target repository without user interaction.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

def load_agent_definition(agent_name: str) -> str:
    """Load agent definition from .claude/agents/"""
    agent_path = Path(__file__).parent / ".claude" / "agents" / f"{agent_name}.md"
    if not agent_path.exists():
        raise FileNotFoundError(f"Agent not found: {agent_path}")
    return agent_path.read_text()


def gather_repo_context(repo_path: str) -> dict:
    """Gather basic context about the target repository"""
    repo = Path(repo_path)

    context = {
        "path": str(repo),
        "name": repo.name,
        "claude_md": "",
        "readme": "",
        "structure": []
    }

    # Load CLAUDE.md if exists
    claude_file = repo / "CLAUDE.md"
    if claude_file.exists():
        context["claude_md"] = claude_file.read_text()

    # Load README if exists
    for readme in ["README.md", "readme.md", "README"]:
        readme_file = repo / readme
        if readme_file.exists():
            context["readme"] = readme_file.read_text()
            break

    # Get basic file structure (top level)
    try:
        context["structure"] = [str(p.relative_to(repo)) for p in repo.rglob("*") if p.is_file()][:50]
    except:
        pass

    return context

def run_reporter_agent(target_repo: str):
    """Run the reporter agent against a target repository"""

    print(f"\n{'='*60}")
    print(f"Running Reporter Agent")
    print(f"Target: {target_repo}")
    print(f"{'='*60}\n")

    # Load agent definition
    print("Loading reporter agent...")
    agent_def = load_agent_definition("reporter")

    # Gather repository context
    print("Gathering repository context...")
    context = gather_repo_context(target_repo)

    # Build the prompt - let the agent handle loading the skill
    prompt = f"""You are executing autonomously. Follow your workflow exactly as defined.

{agent_def}

TARGET REPOSITORY PATH: {context['path']}

REPOSITORY CONTEXT:

CLAUDE.md:
{context['claude_md'] if context['claude_md'] else "No CLAUDE.md found"}

README.md:
{context['readme'][:2000] if context['readme'] else "No README found"}

FILE STRUCTURE (sample):
{chr(10).join(context['structure'][:30])}

Execute your workflow now. Load the skill as defined, analyze the repository, and generate the 22A report.
Output ONLY the final report content in markdown format.
"""

    # Call Claude API
    print("Generating report with Claude...")
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    report_content = response.content[0].text

    # Extract content from <write> tag if present
    if "<write>" in report_content and "</write>" in report_content:
        # Find the content between <write> tags
        start = report_content.find("<write>")
        end = report_content.find("</write>", start)
        if start != -1 and end != -1:
            # Extract everything after the first line (file path) until </write>
            write_block = report_content[start:end]
            lines = write_block.split('\n')
            # Skip first two lines (<write> tag and file path), take rest
            if len(lines) > 2:
                report_content = '\n'.join(lines[2:])

    # Save the report
    output_dir = Path(target_repo) / "docs" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "form-22a.md"

    output_file.write_text(report_content)

    print(f"\n{'='*60}")
    print(f"✅ Report Generated Successfully!")
    print(f"📄 Saved to: {output_file}")
    print(f"{'='*60}\n")

    # Show preview
    print("Preview (first 500 chars):")
    print("-" * 60)
    print(report_content[:500])
    print("...")
    print("-" * 60)

if __name__ == "__main__":
    target_repo = "/Users/mpaz/workspace/joe/ai-fundraising-v2"
    run_reporter_agent(target_repo)
