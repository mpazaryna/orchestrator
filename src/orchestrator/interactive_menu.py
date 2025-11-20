#!/usr/bin/env python3
"""
Interactive menu system for selecting skills, repositories, and agents
Clean, simple text-based menus with no extra noise
"""

import sys
from typing import List, Optional, Tuple
from .config import ConfigLoader, SkillConfig, RepoConfig, AgentConfig


def clear_screen():
    """Clear terminal screen."""
    print("\033[2J\033[H", end="")


def print_header(title: str, width: int = 60) -> None:
    """Print a clean header."""
    print(f"\n{'─' * width}")
    print(f"  {title}")
    print(f"{'─' * width}\n")


def print_menu_item(number: int, title: str, description: str = "", indent: int = 4) -> None:
    """Print a menu item."""
    prefix = " " * indent
    print(f"  {number:2}. {title}")
    if description:
        print(f"{prefix}   {description}")


class InteractiveMenu:
    """Clean, simple text-based menu system."""

    def __init__(self, config_loader: ConfigLoader):
        self.config = config_loader

    def select_skill(self) -> Optional[SkillConfig]:
        """Select a skill from menu."""
        skills = list(self.config.skills.values())
        if not skills:
            print("❌ No skills available")
            return None

        print_header("SELECT SKILL")

        for i, skill in enumerate(skills, 1):
            print_menu_item(i, skill.name, skill.description)

        print(f"\n  q. Cancel\n")

        try:
            choice = input("Select (1-{}, q): ".format(len(skills))).strip().lower()
            if choice == 'q':
                return None

            idx = int(choice) - 1
            if 0 <= idx < len(skills):
                return skills[idx]
            else:
                print(f"❌ Invalid selection")
                return self.select_skill()
        except (ValueError, KeyboardInterrupt):
            return None

    def select_repositories(self) -> Optional[List[RepoConfig]]:
        """Select repositories from menu (multi-select)."""
        repos = list(self.config.repositories.values())
        if not repos:
            print("❌ No repositories configured")
            return None

        print_header("SELECT REPOSITORIES (multi-select)")

        for i, repo in enumerate(repos, 1):
            status = "✓" if repo.active else "✗"
            print_menu_item(i, f"{status} {repo.name}", repo.description)

        print(f"\n  Options:")
        print(f"    • Enter numbers: 1,2,4")
        print(f"    • All: a")
        print(f"    • Cancel: q\n")

        try:
            choice = input("Select (e.g., 1,2 or a): ").strip().lower()

            if choice == 'q':
                return None

            if choice == 'a':
                return list(self.config.get_active_repos())

            selections = [int(x.strip()) - 1 for x in choice.split(',')]
            selected = []
            for idx in selections:
                if 0 <= idx < len(repos):
                    selected.append(repos[idx])

            if not selected:
                print("❌ No valid selections")
                return self.select_repositories()

            return selected

        except (ValueError, KeyboardInterrupt):
            return None

    def select_agent(self) -> Optional[AgentConfig]:
        """Select an agent from menu."""
        agents = list(self.config.agents.values())
        if not agents:
            print("❌ No agents available")
            return None

        print_header("SELECT AGENT (optional)")

        for i, agent in enumerate(agents, 1):
            print_menu_item(i, agent.name, agent.description)

        print(f"\n  s. Skip (no agent)\n")

        try:
            choice = input("Select (1-{}, s): ".format(len(agents))).strip().lower()
            if choice == 's':
                return None

            idx = int(choice) - 1
            if 0 <= idx < len(agents):
                return agents[idx]
            else:
                print(f"❌ Invalid selection")
                return self.select_agent()
        except (ValueError, KeyboardInterrupt):
            return None

    def confirm(self, message: str) -> bool:
        """Get yes/no confirmation."""
        choice = input(f"\n{message} (y/n): ").strip().lower()
        return choice == 'y'


def main_interactive_menu() -> Optional[dict]:
    """Main interactive menu workflow."""
    config = ConfigLoader()
    menu = InteractiveMenu(config)

    print("\n╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  🎯 ORCHESTRATOR - Interactive Mode".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")

    # Select skill
    skill = menu.select_skill()
    if not skill:
        print("\n❌ Cancelled")
        return None

    # Select repos
    repos = menu.select_repositories()
    if not repos:
        print("\n❌ Cancelled")
        return None

    # Select agent (optional)
    agent = menu.select_agent()

    # Display summary
    print_header("READY TO EXECUTE")
    print(f"  Skill:         {skill.name}")
    print(f"  Repositories:  {', '.join([r.name for r in repos])}")
    if agent:
        print(f"  Agent:         {agent.name}")
    print()

    if not menu.confirm("Continue?"):
        print("\n❌ Cancelled")
        return None

    repo_names = [repo.name for repo in repos]
    command = f"uv run python orchestrator.py --skill {skill.name} --repo-names {' '.join(repo_names)}"

    return {
        "skill": skill,
        "repositories": repos,
        "agent": agent,
        "command": command
    }


def get_skill_command(skill_name: str, repo_names: List[str]) -> str:
    """
    Generate orchestrator command from selections.

    Args:
        skill_name: Name of the skill
        repo_names: List of repository names

    Returns:
        Command string for orchestrator
    """
    repos_arg = " ".join(repo_names)
    return f"uv run python orchestrator.py --skill {skill_name} --repo-names {repos_arg}"


def main_interactive():
    """Main interactive menu for CLI invocation."""
    config = ConfigLoader()
    menu = InteractiveMenu(config)

    print("\n╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  🎯 Orchestrator Interactive Menu".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝\n")

    result = menu.select_skill_and_repos()

    if result is None:
        print("\n❌ Selection cancelled")
        return None

    skill, repos = result

    # Display summary
    menu.display_selection_summary(skill, repos)

    # Generate command
    repo_names = [repo.name for repo in repos]
    command = get_skill_command(skill.name, repo_names)

    print(f"\nGenerated command:")
    print(f"  {command}")

    return {
        "skill": skill,
        "repositories": repos,
        "command": command
    }


if __name__ == "__main__":
    result = main_interactive()
    if result:
        print(f"\n✅ Ready to run!")
