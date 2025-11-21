"""
GitHub PM Analysis Tools

Exposes the github-pm-analyzer agent as MCP tools.
"""

from fastmcp import FastMCP


def register_tools(mcp: FastMCP, config_loader, python_runner):
    """Register github-pm tools with the MCP server."""

    @mcp.tool()
    def analyze_issue_trends(
        baseline_snapshot: str,
        current_snapshot: str
    ) -> dict:
        """
        Compare two GitHub issue snapshots to identify trends.

        Args:
            baseline_snapshot: Earlier snapshot folder name (e.g., "2025-01-17_09-30")
            current_snapshot: More recent snapshot folder name (e.g., "2025-01-17_14-15")

        Returns:
            dict with insights, overall_changes, state_changes, and markdown report
        """
        agent_config = config_loader.get_agent("github-pm-analyzer")
        if not agent_config:
            return {"status": "error", "message": "github-pm-analyzer agent not found"}

        return python_runner.run_agent(
            agent_config=agent_config.__dict__,
            task_config={
                "task": "trend_analysis",
                "baseline_snapshot": baseline_snapshot,
                "current_snapshot": current_snapshot
            }
        )

    @mcp.tool()
    def get_daily_activity(days: int = 7) -> dict:
        """
        Generate multi-repo daily/weekly activity report.

        Analyzes commits across all configured repositories.

        Args:
            days: Number of days to look back (default: 7)

        Returns:
            dict with totals, repositories, and markdown report
        """
        agent_config = config_loader.get_agent("github-pm-analyzer")
        if not agent_config:
            return {"status": "error", "message": "github-pm-analyzer agent not found"}

        return python_runner.run_agent(
            agent_config=agent_config.__dict__,
            task_config={
                "task": "daily_activity",
                "days": days
            }
        )

    @mcp.tool()
    def sync_github_repos(dry_run: bool = True) -> dict:
        """
        Sync repositories from GitHub and apply filters.

        Args:
            dry_run: Preview without writing (default: True)

        Returns:
            dict with stats and filtered repository list
        """
        agent_config = config_loader.get_agent("github-pm-analyzer")
        if not agent_config:
            return {"status": "error", "message": "github-pm-analyzer agent not found"}

        return python_runner.run_agent(
            agent_config=agent_config.__dict__,
            task_config={
                "task": "sync_repos",
                "dry_run": dry_run
            }
        )

    @mcp.tool()
    def list_issue_snapshots() -> dict:
        """
        List available issue data snapshots for trend analysis.

        Returns:
            dict with list of snapshot folder names
        """
        agent_config = config_loader.get_agent("github-pm-analyzer")
        if not agent_config:
            return {"status": "error", "message": "github-pm-analyzer agent not found"}

        return python_runner.run_agent(
            agent_config=agent_config.__dict__,
            task_config={"task": "list_snapshots"}
        )
