"""
Synthetic SOAP Notes Generation Tools

Exposes the synth-notes-generator agent as MCP tools.
"""

from fastmcp import FastMCP


def register_tools(mcp: FastMCP, config_loader, python_runner):
    """Register synth-notes tools with the MCP server."""

    @mcp.tool()
    def generate_soap_notes(
        prompt_type: str,
        total: int = 10,
        batch_size: int = 2
    ) -> dict:
        """
        Generate synthetic clinical SOAP notes for training datasets.

        Args:
            prompt_type: Type of clinical scenario. Options:
                - Adult: adult_neck_pain, adult_chronic_lbp, adult_trauma, adult_sports_injury
                - Pediatric: torticollis, plagiocephaly, feeding, wellness
            total: Total number of notes to generate (default: 10)
            batch_size: Notes per API call (default: 2)

        Returns:
            dict with batch_folder, notes_generated, files_created, and usage/cost info
        """
        agent_config = config_loader.get_agent("synth-notes-generator")
        if not agent_config:
            return {"status": "error", "message": "synth-notes-generator agent not found"}

        result = python_runner.run_agent(
            agent_config=agent_config.__dict__,
            task_config={
                "prompt_type": prompt_type,
                "total": total,
                "batch_size": batch_size
            }
        )

        return result

    @mcp.tool()
    def list_soap_prompt_types() -> dict:
        """
        List available prompt types for SOAP note generation.

        Returns:
            dict with adult and pediatric prompt type options
        """
        return {
            "adult": [
                {"id": "adult_neck_pain", "description": "Neck pain, cervicalgia, tech neck"},
                {"id": "adult_chronic_lbp", "description": "Chronic low back pain, degenerative conditions"},
                {"id": "adult_trauma", "description": "Acute trauma, MVA, falls, work injuries"},
                {"id": "adult_sports_injury", "description": "Sports injuries, athletic performance"}
            ],
            "pediatric": [
                {"id": "torticollis", "description": "Infant torticollis"},
                {"id": "plagiocephaly", "description": "Cranial asymmetry"},
                {"id": "feeding", "description": "Feeding difficulties"},
                {"id": "wellness", "description": "General wellness exams"}
            ]
        }
