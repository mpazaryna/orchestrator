"""
Agent Runner - Executes skills as autonomous agents with tool use
"""

from typing import Dict, Any, List
from pathlib import Path
from anthropic import Anthropic
from .agent_tools import ToolExecutor, get_tool_definitions
import json


class AgentRunner:
    """Runs Claude agents with tool use capability."""

    def __init__(self, client: Anthropic, max_iterations: int = 25):
        """
        Initialize agent runner.

        Args:
            client: Anthropic API client
            max_iterations: Maximum number of agent turns to prevent infinite loops
        """
        self.client = client
        self.max_iterations = max_iterations

    def run_agent(
        self,
        repo_path: str,
        skill: Dict[str, Any],
        initial_context: str = ""
    ) -> Dict[str, Any]:
        """
        Run an agent with tool use capabilities.

        Args:
            repo_path: Path to the repository
            skill: Skill metadata dict
            initial_context: Additional context about the repository

        Returns:
            dict with execution results and metadata
        """
        repo_name = Path(repo_path).name
        tool_executor = ToolExecutor(repo_path)
        tools = get_tool_definitions()

        # Build initial prompt
        system_prompt = self._build_system_prompt(skill)
        initial_message = self._build_initial_message(repo_name, repo_path, initial_context, skill)

        # Initialize conversation
        messages = [{"role": "user", "content": initial_message}]

        # Track execution
        iteration = 0
        files_created = []
        files_modified = []
        tool_uses = []

        print(f"Starting agentic loop for '{skill['name']}'...")

        while iteration < self.max_iterations:
            iteration += 1
            print(f"  Iteration {iteration}...")

            # Call Claude with tool use
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                system=system_prompt,
                tools=tools,
                messages=messages
            )

            # Check stop reason
            if response.stop_reason == "end_turn":
                # Agent finished
                print(f"  Agent completed after {iteration} iterations")
                break

            # Process response content
            assistant_message = {"role": "assistant", "content": response.content}
            messages.append(assistant_message)

            # Check if there are tool uses
            tool_results = []
            has_tool_use = False

            for block in response.content:
                if block.type == "tool_use":
                    has_tool_use = True
                    tool_name = block.name
                    tool_input = block.input
                    tool_id = block.id

                    print(f"    Tool: {tool_name}")

                    # Execute tool
                    result = tool_executor.execute_tool(tool_name, tool_input)

                    # Track file operations
                    if tool_name == "write_file" and "success" in result:
                        if tool_input["path"] in files_modified:
                            pass  # Already tracked
                        else:
                            files_created.append(tool_input["path"])
                            files_modified.append(tool_input["path"])

                    tool_uses.append({
                        "iteration": iteration,
                        "tool": tool_name,
                        "input": tool_input,
                        "result": result
                    })

                    # Add tool result to conversation
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": json.dumps(result)
                    })

            if has_tool_use:
                # Send tool results back to agent
                messages.append({"role": "user", "content": tool_results})
            else:
                # No tool use and no explicit end - agent might be done
                print(f"  Agent stopped without tool use")
                break

        if iteration >= self.max_iterations:
            print(f"  Warning: Agent reached max iterations ({self.max_iterations})")

        return {
            "iterations": iteration,
            "files_created": files_created,
            "files_modified": files_modified,
            "tool_uses": tool_uses,
            "conversation_length": len(messages)
        }

    def _build_system_prompt(self, skill: Dict[str, Any]) -> str:
        """Build system prompt for the agent."""
        return f"""You are an autonomous agent executing a skill from a developer's toolkit.

SKILL DEFINITION:
{skill['definition']}

You have access to tools to read, write, list, and search files in the repository.

IMPORTANT INSTRUCTIONS:
1. Use the tools to explore the repository and understand its structure
2. Follow the skill definition carefully to complete the task
3. Create all necessary files and directories as specified in the skill
4. When you are done, simply stop - do not ask for confirmation
5. Work autonomously - you have full authority to create and modify files

Be thorough and complete the entire task as defined in the skill."""

    def _build_initial_message(
        self,
        repo_name: str,
        repo_path: str,
        initial_context: str,
        skill: Dict[str, Any]
    ) -> str:
        """Build initial user message to start the agent."""
        parts = [
            f"Please execute the '{skill['name']}' skill on this repository.",
            "",
            f"Repository: {repo_name}",
            f"Path: {repo_path}",
        ]

        if initial_context:
            parts.extend([
                "",
                "Repository Context:",
                initial_context
            ])

        if skill.get('template'):
            parts.extend([
                "",
                "Template/Structure Reference:",
                skill['template']
            ])

        parts.extend([
            "",
            "Use the available tools to explore the repository and complete the task.",
            "Create all necessary files as specified in the skill definition."
        ])

        return "\n".join(parts)
