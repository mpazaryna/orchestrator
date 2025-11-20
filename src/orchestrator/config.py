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


class ConfigLoader:
    """Loads and manages repository configuration."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config loader.

        Args:
            config_path: Path to repos.json file. Defaults to repos.json in project root.
        """
        if config_path is None:
            # Default to repos.json in project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "repos.json"

        self.config_path = Path(config_path)
        self.config_data = self._load_config()
        self.repositories = self._parse_repositories()
        self.groups = self.config_data.get("groups", {})

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            return {"repositories": [], "groups": {}}

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _parse_repositories(self) -> Dict[str, RepoConfig]:
        """Parse repository configurations."""
        repos = {}
        for repo_data in self.config_data.get("repositories", []):
            repo = RepoConfig(repo_data)
            repos[repo.name] = repo
        return repos

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
