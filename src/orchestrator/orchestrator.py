#!/usr/bin/env python3
"""
Orchestrator - Run Python agents from the command line

Focused on executing autonomous Python agents that return structured results.
MCP server is the primary interface; this CLI is for direct agent execution.
"""

import argparse
import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

from .config import ConfigLoader
from .python_agent_runner import PythonAgentRunner

# Load environment variables
load_dotenv()

# Initialize
config_loader = ConfigLoader()


def get_client() -> Anthropic:
    """Get Anthropic client."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")
    return Anthropic(api_key=api_key)


def run_agent(agent_name: str, task_config: dict) -> dict:
    """
    Run a Python agent with the given configuration.

    Args:
        agent_name: Name of the agent from agents.json
        task_config: Task-specific configuration

    Returns:
        dict with execution results
    """
    agent_config = config_loader.get_agent(agent_name)
    if not agent_config:
        return {"status": "error", "message": f"Agent '{agent_name}' not found"}

    if agent_config.type != "python":
        return {"status": "error", "message": f"Agent '{agent_name}' is not a Python agent (type: {agent_config.type})"}

    print(f"\n{'='*60}")
    print(f"Running: {agent_name}")
    print(f"Description: {agent_config.description}")
    print(f"{'='*60}\n")

    client = get_client()
    runner = PythonAgentRunner(client)

    return runner.run_agent(
        agent_config=agent_config.__dict__,
        task_config=task_config
    )


def list_agents():
    """List all available agents."""
    print("\nAvailable Agents:")
    print("=" * 80)

    for agent_name in sorted(config_loader.list_agents()):
        agent = config_loader.get_agent(agent_name)
        tags = f" [{', '.join(agent.tags)}]" if agent.tags else ""
        print(f"\n  {agent_name} ({agent.type})")
        print(f"    {agent.description}")
        print(f"    Capabilities: {', '.join(agent.capabilities)}{tags}")

    print(f"\n  Total: {len(config_loader.list_agents())} agents")
    print("=" * 80)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Orchestrator - Run autonomous Python agents"
    )

    parser.add_argument(
        "--list-agents",
        action="store_true",
        help="List all available agents"
    )

    parser.add_argument(
        "--agent", "-a",
        type=str,
        help="Agent to run (e.g., synth-notes-generator, github-pm-analyzer)"
    )

    parser.add_argument(
        "--task", "-t",
        type=str,
        help="Task to execute (agent-specific)"
    )

    parser.add_argument(
        "--config", "-c",
        type=str,
        help="JSON config for the task (e.g., '{\"days\": 7}')"
    )

    # Convenience args for common agents
    parser.add_argument("--prompt-type", type=str, help="For synth-notes: prompt type")
    parser.add_argument("--total", type=int, help="For synth-notes: total to generate")
    parser.add_argument("--batch-size", type=int, help="For synth-notes: batch size")
    parser.add_argument("--days", type=int, help="For github-pm: days to analyze")
    parser.add_argument("--baseline", type=str, help="For github-pm: baseline snapshot")
    parser.add_argument("--current", type=str, help="For github-pm: current snapshot")

    args = parser.parse_args()

    if args.list_agents:
        list_agents()
        return 0

    if not args.agent:
        parser.print_help()
        print("\n\nExamples:")
        print("  # List agents")
        print("  uv run python -m orchestrator --list-agents")
        print("")
        print("  # Generate SOAP notes")
        print("  uv run python -m orchestrator -a synth-notes-generator --prompt-type adult_neck_pain --total 5")
        print("")
        print("  # Get GitHub activity")
        print("  uv run python -m orchestrator -a github-pm-analyzer --task daily_activity --days 7")
        print("")
        print("  # List issue snapshots")
        print("  uv run python -m orchestrator -a github-pm-analyzer --task list_snapshots")
        return 1

    # Build task config
    task_config = {}

    # Parse JSON config if provided
    if args.config:
        try:
            task_config = json.loads(args.config)
        except json.JSONDecodeError as e:
            print(f"Error parsing --config JSON: {e}")
            return 1

    # Add task if specified
    if args.task:
        task_config["task"] = args.task

    # Add convenience args
    if args.prompt_type:
        task_config["prompt_type"] = args.prompt_type
    if args.total:
        task_config["total"] = args.total
    if args.batch_size:
        task_config["batch_size"] = args.batch_size
    if args.days:
        task_config["days"] = args.days
    if args.baseline:
        task_config["baseline_snapshot"] = args.baseline
    if args.current:
        task_config["current_snapshot"] = args.current

    # Run the agent
    result = run_agent(args.agent, task_config)

    # Output result
    if result.get("status") == "success":
        print("\n✅ Success!")
        # Print key info based on what's in the result
        if "notes_generated" in result:
            print(f"   Notes generated: {result['notes_generated']}")
        if "batch_folder" in result:
            print(f"   Batch folder: {result['batch_folder']}")
        if "usage" in result:
            print(f"   Cost: ${result['usage'].get('total_cost', 'N/A')}")
        if "insights" in result:
            print(f"   Insights: {len(result['insights'])}")
        if "totals" in result:
            print(f"   Total commits: {result['totals'].get('commits', 'N/A')}")
        if "snapshots" in result:
            print(f"   Snapshots: {result['total']}")
            for s in result["snapshots"][:5]:
                print(f"     - {s}")
        if "report" in result:
            print("\n--- Report Preview ---")
            print(result["report"][:500] + "..." if len(result.get("report", "")) > 500 else result.get("report", ""))
    else:
        print(f"\n❌ Error: {result.get('message', 'Unknown error')}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
