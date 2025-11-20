#!/usr/bin/env python3
"""
Generic Orchestrator for Claude Skills
Runs any skill from your toolkit against multiple local repositories
"""

import subprocess
import json
import os
import argparse
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv
from .agent_runner import AgentRunner

# Load environment variables from .env file
load_dotenv()

# Configuration
SKILLS_BASE_PATH = "/Users/mpaz/workspace/claude-toolkit/generated-skills"

# Default repositories (can be overridden via config or CLI)
DEFAULT_REPOS = [
    "/Users/mpaz/workspace/mcp-fleet",
    "/Users/mpaz/workspace/rishi",
]

# Initialize Anthropic client
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError(
        "ANTHROPIC_API_KEY not found. Please set it in your .env file or environment variables."
    )
client = Anthropic(api_key=api_key)

def collect_repo_context(repo_path: Path) -> str:
    """
    Collect relevant information about the repository for analysis.

    Args:
        repo_path: Path to the repository

    Returns:
        String containing repository context
    """
    context_parts = []

    # Add directory structure
    try:
        result = subprocess.run(
            ["find", ".", "-type", "f", "-not", "-path", "*/.*", "-not", "-path", "*/node_modules/*",
             "-not", "-path", "*/__pycache__/*", "-not", "-path", "*/venv/*", "-not", "-path", "*/.venv/*"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            files = result.stdout.strip().split('\n')[:100]  # Limit to first 100 files
            context_parts.append("=== Repository Structure ===\n" + "\n".join(files))
    except Exception as e:
        context_parts.append(f"Could not get directory structure: {e}")

    # Read important files
    important_files = ["README.md", "package.json", "pyproject.toml", "requirements.txt",
                       "Cargo.toml", "go.mod", "pom.xml", "build.gradle"]

    for filename in important_files:
        filepath = repo_path / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read(5000)  # Limit content
                    context_parts.append(f"\n=== {filename} ===\n{content}")
            except Exception as e:
                context_parts.append(f"\nCould not read {filename}: {e}")

    return "\n".join(context_parts)

def load_skill(skill_name: str) -> dict:
    """
    Load a skill from the toolkit.

    Args:
        skill_name: Name of the skill (directory name)

    Returns:
        dict with skill metadata and content
    """
    skill_path = Path(SKILLS_BASE_PATH) / skill_name

    if not skill_path.exists():
        raise ValueError(f"Skill '{skill_name}' not found at {skill_path}")

    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        raise ValueError(f"SKILL.md not found for '{skill_name}'")

    with open(skill_file, 'r', encoding='utf-8') as f:
        skill_definition = f.read()

    # Check for optional template file
    template_file = skill_path / "template.md"
    template = None
    if template_file.exists():
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()

    # Extract metadata from skill definition
    metadata = extract_skill_metadata(skill_definition)

    return {
        "name": skill_name,
        "path": str(skill_path),
        "definition": skill_definition,
        "template": template,
        "metadata": metadata
    }

def extract_skill_metadata(skill_definition: str) -> dict:
    """
    Extract metadata from skill definition to understand output expectations.

    Args:
        skill_definition: The SKILL.md content

    Returns:
        dict with metadata like output_location, output_type, etc.
    """
    metadata = {
        "output_location": None,
        "output_filename": None,
        "creates_directory": False
    }

    # Look for common patterns in the skill definition
    lower_def = skill_definition.lower()

    # Check for specific output directory patterns
    if "docs/moc/" in lower_def or "`docs/moc/`" in skill_definition:
        metadata["output_location"] = "docs/moc"
        metadata["creates_directory"] = True
    elif "output is written to" in lower_def:
        # Try to extract the path mentioned after this phrase
        import re
        match = re.search(r'output is written to[:\s]+[`"]?([^`"\s\n]+)', skill_definition, re.IGNORECASE)
        if match:
            metadata["output_location"] = match.group(1).strip("`\"")

    # Check for specific output filename patterns
    if "project.md" in lower_def:
        metadata["output_filename"] = "PROJECT.md"

    return metadata

def run_skill_on_repo(repo_path: str, skill: dict) -> str:
    """
    Use Claude to run a skill on a repository.

    Args:
        repo_path: Path to the repository to analyze
        skill: Skill metadata dict from load_skill()

    Returns:
        Generated output from the skill
    """
    repo_path_obj = Path(repo_path)

    # Collect repository context
    repo_context = collect_repo_context(repo_path_obj)

    # Build the prompt
    prompt_parts = [
        f"You are executing the '{skill['name']}' skill. Your task is to analyze this code repository and produce output according to the skill definition.",
        "",
        "=== SKILL DEFINITION ===",
        skill['definition'],
        "",
        "=== REPOSITORY TO ANALYZE ===",
        f"Repository Name: {repo_path_obj.name}",
        f"Repository Path: {repo_path}",
        "",
        "=== REPOSITORY INFORMATION ===",
        repo_context,
    ]

    # Add template if available
    if skill['template']:
        prompt_parts.extend([
            "",
            "=== TEMPLATE STRUCTURE ===",
            skill['template'],
        ])

    prompt_parts.extend([
        "",
        "=== INSTRUCTIONS ===",
        "Follow the skill definition above and produce the appropriate output for this repository.",
        "Return ONLY the generated content, no additional commentary."
    ])

    prompt = "\n".join(prompt_parts)

    # Call Claude API
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text

def process_repo_with_skill(repo_path: str, skill: dict, output_filename: str = None, use_agent: bool = True) -> dict:
    """
    Process a repository with a given skill.

    Args:
        repo_path: Path to the repository
        skill: Skill metadata dict from load_skill()
        output_filename: Optional custom output filename (overrides skill defaults)
        use_agent: If True, run as autonomous agent with tools. If False, use simple prompt mode.

    Returns:
        dict with repo info and result
    """
    repo_name = Path(repo_path).name
    repo_path_obj = Path(repo_path)

    print(f"\n{'='*60}")
    print(f"Processing: {repo_name}")
    print(f"Path: {repo_path}")
    print(f"Skill: {skill['name']}")
    print(f"Mode: {'Agent' if use_agent else 'Simple'}")
    print(f"{'='*60}")

    try:
        # Check if repo exists
        if not repo_path_obj.exists():
            return {
                "repo": repo_name,
                "path": repo_path,
                "skill": skill['name'],
                "status": "error",
                "message": "Path does not exist"
            }

        if use_agent:
            # Run as autonomous agent with tool use
            print(f"Running '{skill['name']}' as autonomous agent...")

            # Collect initial context
            initial_context = collect_repo_context(repo_path_obj)

            # Run agent
            agent_runner = AgentRunner(client)
            execution_result = agent_runner.run_agent(repo_path, skill, initial_context)

            return {
                "repo": repo_name,
                "path": repo_path,
                "skill": skill['name'],
                "status": "success",
                "mode": "agent",
                "iterations": execution_result["iterations"],
                "files_created": execution_result["files_created"],
                "files_modified": execution_result["files_modified"],
                "tool_uses_count": len(execution_result["tool_uses"]),
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Use simple prompt mode (legacy)
            print(f"Running '{skill['name']}' in simple mode...")
            skill_output = run_skill_on_repo(repo_path, skill)

            # Determine output location using skill metadata
            metadata = skill['metadata']

            if output_filename:
                # User override takes precedence
                output_file = repo_path_obj / output_filename
            elif metadata['output_location'] and metadata['creates_directory']:
                # Skill specifies a directory (like docs/moc/)
                output_dir = repo_path_obj / metadata['output_location']
                output_dir.mkdir(parents=True, exist_ok=True)
                # For directory-based output, save as README.md or skill-specific name
                output_file = output_dir / (metadata.get('output_filename') or 'README.md')
                print(f"Creating directory structure: {metadata['output_location']}")
            elif metadata['output_filename']:
                # Skill specifies a specific filename
                output_file = repo_path_obj / metadata['output_filename']
            else:
                # Fallback to skill name-based output
                if skill['name'] == 'repo-summarizer':
                    output_filename = "PROJECT.md"
                else:
                    output_filename = f"{skill['name']}_output.md"
                output_file = repo_path_obj / output_filename

            # Save output
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(skill_output)

            print(f"Generated output at: {output_file}")

            return {
                "repo": repo_name,
                "path": repo_path,
                "skill": skill['name'],
                "status": "success",
                "mode": "simple",
                "output_file": str(output_file),
                "preview": skill_output[:500] + "..." if len(skill_output) > 500 else skill_output,
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        return {
            "repo": repo_name,
            "path": repo_path,
            "skill": skill['name'],
            "status": "error",
            "message": str(e)
        }

def list_available_skills():
    """List all available skills in the toolkit."""
    skills_dir = Path(SKILLS_BASE_PATH)
    if not skills_dir.exists():
        print(f"Skills directory not found: {SKILLS_BASE_PATH}")
        return []

    skills = []
    for item in sorted(skills_dir.iterdir()):
        if item.is_dir() and (item / "SKILL.md").exists():
            skills.append(item.name)

    return skills

def main():
    """Main orchestrator function"""
    parser = argparse.ArgumentParser(
        description="Generic Orchestrator for Claude Skills - Run any skill against multiple repositories"
    )
    parser.add_argument(
        "--skill",
        "-s",
        type=str,
        default="repo-summarizer",
        help="Name of the skill to run (default: repo-summarizer)"
    )
    parser.add_argument(
        "--list-skills",
        action="store_true",
        help="List all available skills"
    )
    parser.add_argument(
        "--repos",
        "-r",
        nargs="+",
        help="Repository paths to process (overrides default)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Custom output filename (default varies by skill)"
    )
    parser.add_argument(
        "--agent",
        "-a",
        action="store_true",
        default=True,
        help="Run as autonomous agent with tool use (default: True)"
    )
    parser.add_argument(
        "--simple",
        action="store_true",
        help="Run in simple prompt mode (no tool use)"
    )

    args = parser.parse_args()

    # Determine execution mode
    use_agent = not args.simple

    # List skills if requested
    if args.list_skills:
        print("\nAvailable Skills:")
        print("=" * 60)
        skills = list_available_skills()
        for skill in skills:
            print(f"  - {skill}")
        print(f"\nTotal: {len(skills)} skills")
        print("=" * 60)
        return

    # Load the skill
    try:
        skill = load_skill(args.skill)
    except ValueError as e:
        print(f"\nError: {e}")
        print("\nRun with --list-skills to see available skills")
        return 1

    # Determine repositories to process
    repos = args.repos if args.repos else DEFAULT_REPOS

    print(f"\nGeneric Orchestrator - Starting at {datetime.now()}")
    print(f"Skill: {skill['name']}")
    print(f"Mode: {'Agent (with tool use)' if use_agent else 'Simple (prompt only)'}")
    print(f"Will process {len(repos)} repositories\n")

    results = []

    for repo_path in repos:
        result = process_repo_with_skill(repo_path, skill, args.output, use_agent)
        results.append(result)

        # Print summary
        status_emoji = "Success" if result["status"] == "success" else "Failed"
        print(f"\n{status_emoji}: {result['repo']} - {result['status']}")

        if result["status"] == "success":
            if result.get("mode") == "agent":
                print(f"  Iterations: {result.get('iterations', 'N/A')}")
                print(f"  Files created: {len(result.get('files_created', []))}")
                print(f"  Tool uses: {result.get('tool_uses_count', 'N/A')}")
                if result.get('files_created'):
                    print(f"  Created: {', '.join(result['files_created'][:5])}")
            elif "output_file" in result:
                print(f"  Output created at: {result['output_file']}")
        elif result["status"] == "error":
            print(f"  Error: {result.get('message', 'Unknown error')}")

    # Save results to JSON
    output_file = Path.home() / f"orchestrator_{skill['name']}_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Orchestrator Complete!")
    print(f"Results saved to: {output_file}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()