"""
Python Agent Runner

Executes autonomous Python agents that are self-contained and don't require
Claude Code's tool-based execution model.
"""

import sys
import importlib.util
from pathlib import Path
from typing import Dict, Any
from anthropic import Anthropic


class PythonAgentRunner:
    """Runs autonomous Python agents."""

    def __init__(self, client: Anthropic):
        """
        Initialize Python agent runner.

        Args:
            client: Anthropic API client to pass to agents
        """
        self.client = client

    def run_agent(
        self,
        agent_config: Dict[str, Any],
        task_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a Python agent.

        Args:
            agent_config: Agent metadata from agents.json
            task_config: Configuration for this specific execution

        Returns:
            dict with execution results from the agent
        """
        agent_path = Path(agent_config['path'])
        agent_module_path = agent_path / "agent.py"

        if not agent_module_path.exists():
            return {
                'status': 'error',
                'message': f"Agent module not found at: {agent_module_path}"
            }

        # Dynamically import the agent module
        spec = importlib.util.spec_from_file_location("agent_module", agent_module_path)
        if spec is None or spec.loader is None:
            return {
                'status': 'error',
                'message': f"Failed to load agent module: {agent_module_path}"
            }

        agent_module = importlib.util.module_from_spec(spec)
        sys.modules["agent_module"] = agent_module
        spec.loader.exec_module(agent_module)

        # Get the agent class from AGENT.json metadata
        agent_metadata_path = agent_path / "AGENT.json"
        if agent_metadata_path.exists():
            import json
            with open(agent_metadata_path) as f:
                metadata = json.load(f)
                agent_class_name = metadata.get('class_name', metadata.get('class'))
        else:
            # Default class name based on agent name
            agent_class_name = self._guess_class_name(agent_config['name'])

        # Get the agent class
        if not hasattr(agent_module, agent_class_name):
            return {
                'status': 'error',
                'message': f"Agent class '{agent_class_name}' not found in module"
            }

        agent_class = getattr(agent_module, agent_class_name)

        # Instantiate the agent
        # Pass API key from client
        api_key = self.client.api_key

        try:
            agent_instance = agent_class(api_key=api_key)
        except TypeError:
            # Agent might not accept api_key parameter
            agent_instance = agent_class()

        # Execute the agent
        print(f"[PythonAgentRunner] Executing {agent_config['name']}...")
        result = agent_instance.execute(task_config)

        return result

    def _guess_class_name(self, agent_name: str) -> str:
        """
        Guess class name from agent name.

        Examples:
            synth-notes-generator -> SynthNotesGeneratorAgent
            research-agent -> ResearchAgent
        """
        # Convert kebab-case to PascalCase
        parts = agent_name.split('-')
        class_name = ''.join(word.capitalize() for word in parts)

        # Add 'Agent' suffix if not present
        if not class_name.endswith('Agent'):
            class_name += 'Agent'

        return class_name
