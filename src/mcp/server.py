"""
Orchestrator MCP Server

Exposes orchestrator agents as MCP tools accessible from any Claude Code session.
Tools are organized in modular folders under tools/.
"""

from fastmcp import FastMCP
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))  # orchestrator
sys.path.insert(0, str(Path(__file__).parent))  # mcp (for tools imports)

from orchestrator.python_agent_runner import PythonAgentRunner
from orchestrator.config import ConfigLoader
from anthropic import Anthropic
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Initialize core components
config_loader = ConfigLoader()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
python_runner = PythonAgentRunner(client)

# Initialize MCP server
mcp = FastMCP("orchestrator")


# =============================================================================
# Register tool modules
# =============================================================================

from tools.synth_notes import register_tools as register_synth_notes
register_synth_notes(mcp, config_loader, python_runner)

from tools.github_pm import register_tools as register_github_pm
register_github_pm(mcp, config_loader, python_runner)


# =============================================================================
# Core orchestrator tools (always available)
# =============================================================================

@mcp.tool()
def list_agents() -> dict:
    """
    List all available agents in the orchestrator.

    Returns:
        dict with list of agent names and their descriptions
    """
    agents = []
    for agent_name in config_loader.list_agents():
        agent = config_loader.get_agent(agent_name)
        agents.append({
            "name": agent_name,
            "description": agent.description,
            "type": agent.type,
            "capabilities": agent.capabilities
        })

    return {"agents": agents, "total": len(agents)}


@mcp.tool()
def list_skills() -> dict:
    """
    List all available skills in the orchestrator.

    Returns:
        dict with list of skill names and their descriptions
    """
    skills = []
    for skill_name in config_loader.list_skills():
        skill = config_loader.get_skill(skill_name)
        skills.append({
            "name": skill_name,
            "description": skill.description,
            "mode": skill.mode,
            "tags": skill.tags
        })

    return {"skills": skills, "total": len(skills)}


if __name__ == "__main__":
    mcp.run()
