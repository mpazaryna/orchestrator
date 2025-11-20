"""
Configuration management for orchestrator
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class RepoConfig:
    """Repository configuration."""

    def __init__(self, data: Dict[str, Any]):
        self.name = data["name"]
        self.path = data["path"]
        self.github = data.get("github")
        self.description = data.get("description", "")
        self.tags = data.get("tags", [])
        self.active = data.get("active", True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "github": self.github,
            "description": self.description,
            "tags": self.tags,
            "active": self.active
        }


class SkillConfig:
    """Skill configuration."""

    def __init__(self, data: Dict[str, Any]):
        self.name = data["name"]
        self.description = data.get("description", "")
        self.path = data["path"]
        self.mode = data.get("mode", "agent")
        self.tags = data.get("tags", [])
        self.repo_types = data.get("repo_types", ["any"])
        self.version = data.get("version", "1.0.0")
        self.output = data.get("output", "")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "path": self.path,
            "mode": self.mode,
            "tags": self.tags,
            "repo_types": self.repo_types,
            "version": self.version,
            "output": self.output
        }


class AgentConfig:
    """Agent configuration."""

    def __init__(self, data: Dict[str, Any]):
        self.name = data["name"]
        self.description = data.get("description", "")
        self.path = data["path"]
        self.type = data.get("type", "autonomous")
        self.capabilities = data.get("capabilities", [])
        self.version = data.get("version", "1.0.0")
        self.tags = data.get("tags", [])
        self.output_dir = data.get("output_dir", "")
        self.use_case = data.get("use_case", "")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "path": self.path,
            "type": self.type,
            "capabilities": self.capabilities,
            "version": self.version,
            "tags": self.tags,
            "output_dir": self.output_dir,
            "use_case": self.use_case
        }


class ConfigLoader:
    """Loads and manages repository, skill, and agent configuration."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize config loader.

        Args:
            config_dir: Path to config directory. Defaults to config/ folder in project root.
        """
        if config_dir is None:
            # Default to config/ folder in project root
            project_root = Path(__file__).parent.parent.parent
            config_dir = project_root / "config"

        self.config_dir = Path(config_dir)

        # Load all configurations
        self.repositories = self._load_repositories()
        self.groups = self._load_groups()
        self.skills = self._load_skills()
        self.agents = self._load_agents()

    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load a JSON config file from config directory."""
        config_file = self.config_dir / filename
        if not config_file.exists():
            return {}

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load {filename}: {e}")
            return {}

    def _load_repositories(self) -> Dict[str, RepoConfig]:
        """Load repository configurations from repos.json."""
        config_data = self._load_json("repos.json")
        repos = {}
        for repo_data in config_data.get("repositories", []):
            repo = RepoConfig(repo_data)
            repos[repo.name] = repo
        return repos

    def _load_groups(self) -> Dict[str, List[str]]:
        """Load repository groups from repos.json."""
        config_data = self._load_json("repos.json")
        return config_data.get("groups", {})

    def _load_skills(self) -> Dict[str, SkillConfig]:
        """Load skill configurations from skills.json."""
        config_data = self._load_json("skills.json")
        skills = {}
        for skill_data in config_data.get("skills", []):
            skill = SkillConfig(skill_data)
            skills[skill.name] = skill
        return skills

    def _load_agents(self) -> Dict[str, AgentConfig]:
        """Load agent configurations from agents.json."""
        config_data = self._load_json("agents.json")
        agents = {}
        for agent_data in config_data.get("agents", []):
            agent = AgentConfig(agent_data)
            agents[agent.name] = agent
        return agents

    # Repository methods
    def get_repo(self, name: str) -> Optional[RepoConfig]:
        """Get repository by name."""
        return self.repositories.get(name)

    def get_active_repos(self) -> List[RepoConfig]:
        """Get all active repositories."""
        return [repo for repo in self.repositories.values() if repo.active]

    def get_group(self, group_name: str) -> List[RepoConfig]:
        """Get repositories in a group."""
        repo_names = self.groups.get(group_name, [])
        return [self.repositories[name] for name in repo_names if name in self.repositories]

    def get_repos_by_tag(self, tag: str) -> List[RepoConfig]:
        """Get repositories with a specific tag."""
        return [repo for repo in self.repositories.values() if tag in repo.tags]

    def list_repos(self) -> List[str]:
        """List all repository names."""
        return list(self.repositories.keys())

    def list_groups(self) -> List[str]:
        """List all group names."""
        return list(self.groups.keys())

    def get_repo_paths(self, repo_names: Optional[List[str]] = None) -> List[str]:
        """
        Get repository paths.

        Args:
            repo_names: Optional list of repo names. If None, returns all active repos.

        Returns:
            List of repository paths
        """
        if repo_names is None:
            repos = self.get_active_repos()
        else:
            repos = [self.get_repo(name) for name in repo_names]
            repos = [r for r in repos if r is not None]

        return [repo.path for repo in repos]

    # Skill methods
    def get_skill(self, name: str) -> Optional[SkillConfig]:
        """Get skill by name."""
        return self.skills.get(name)

    def list_skills(self) -> List[str]:
        """List all available skill names."""
        return list(self.skills.keys())

    def get_skills_by_tag(self, tag: str) -> List[SkillConfig]:
        """Get skills with a specific tag."""
        return [skill for skill in self.skills.values() if tag in skill.tags]

    # Agent methods
    def get_agent(self, name: str) -> Optional[AgentConfig]:
        """Get agent by name."""
        return self.agents.get(name)

    def list_agents(self) -> List[str]:
        """List all available agent names."""
        return list(self.agents.keys())
