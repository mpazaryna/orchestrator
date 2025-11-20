"""
Agent Tools - Tool definitions and execution for Claude agents
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, List
import json


class ToolExecutor:
    """Executes tools on behalf of Claude agents within a repository context."""

    def __init__(self, repo_path: str):
        """
        Initialize tool executor for a specific repository.

        Args:
            repo_path: Path to the repository where tools will operate
        """
        self.repo_path = Path(repo_path)
        self.working_directory = self.repo_path

    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool and return the result.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            dict with tool execution result
        """
        try:
            if tool_name == "read_file":
                return self._read_file(tool_input)
            elif tool_name == "write_file":
                return self._write_file(tool_input)
            elif tool_name == "list_files":
                return self._list_files(tool_input)
            elif tool_name == "search_files":
                return self._search_files(tool_input)
            elif tool_name == "run_bash":
                return self._run_bash(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    def _read_file(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Read a file from the repository."""
        file_path = self.repo_path / tool_input["path"]

        if not file_path.exists():
            return {"error": f"File not found: {tool_input['path']}"}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"content": content}
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}

    def _write_file(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Write content to a file in the repository."""
        file_path = self.repo_path / tool_input["path"]

        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(tool_input["content"])
            return {"success": True, "path": str(file_path)}
        except Exception as e:
            return {"error": f"Failed to write file: {str(e)}"}

    def _list_files(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """List files in the repository matching a pattern."""
        pattern = tool_input.get("pattern", "*")
        path = tool_input.get("path", ".")

        search_path = self.repo_path / path

        if not search_path.exists():
            return {"error": f"Path not found: {path}"}

        try:
            if pattern == "*":
                files = list(search_path.rglob("*"))
            else:
                files = list(search_path.rglob(pattern))

            # Filter to only files and make paths relative
            file_list = [
                str(f.relative_to(self.repo_path))
                for f in files
                if f.is_file()
            ]

            # Limit results to avoid overwhelming output
            if len(file_list) > 100:
                file_list = file_list[:100]
                truncated = True
            else:
                truncated = False

            return {
                "files": file_list,
                "count": len(file_list),
                "truncated": truncated
            }
        except Exception as e:
            return {"error": f"Failed to list files: {str(e)}"}

    def _search_files(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Search for a pattern in files using grep."""
        pattern = tool_input["pattern"]
        file_pattern = tool_input.get("file_pattern", "*")

        try:
            # Use grep for text search
            result = subprocess.run(
                ["grep", "-r", "-l", pattern, "."],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                return {"files": files, "count": len(files)}
            elif result.returncode == 1:
                # No matches found
                return {"files": [], "count": 0}
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}

    def _run_bash(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Run a bash command in the repository directory."""
        command = tool_input["command"]

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out after 30 seconds"}
        except Exception as e:
            return {"error": f"Command failed: {str(e)}"}


def get_tool_definitions() -> List[Dict[str, Any]]:
    """
    Get Anthropic API tool definitions for Claude.

    Returns:
        List of tool definition dicts for Claude API
    """
    return [
        {
            "name": "read_file",
            "description": "Read the contents of a file in the repository. Use this to examine existing files.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file within the repository"
                    }
                },
                "required": ["path"]
            }
        },
        {
            "name": "write_file",
            "description": "Write content to a file in the repository. Creates parent directories if needed. Use this to create or overwrite files.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path where the file should be written"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        },
        {
            "name": "list_files",
            "description": "List files in the repository matching a glob pattern. Use this to explore the repository structure.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern to match files (e.g., '*.py', '**/*.md'). Default is '*' for all files."
                    },
                    "path": {
                        "type": "string",
                        "description": "Starting path for the search (relative to repo root). Default is '.'."
                    }
                },
                "required": []
            }
        },
        {
            "name": "search_files",
            "description": "Search for a text pattern in files using grep. Returns list of files containing the pattern.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Text pattern to search for"
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "Optional glob pattern to limit which files to search"
                    }
                },
                "required": ["pattern"]
            }
        },
        {
            "name": "run_bash",
            "description": "Execute a bash command in the repository directory. Use for git operations, running tests, etc.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Bash command to execute"
                    }
                },
                "required": ["command"]
            }
        }
    ]
