# backend/app/service/agents/tools/art_evolution_tool.py
# Source: adk-local-docs/docs/tools/function-tools.md
#
# Tool for fetching the previous tier's art metadata (prompt + tier level)
# to enable visual continuity in the art evolution pipeline.

import logging
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)


def fetch_previous_art_metadata(tool_context: ToolContext) -> dict:
    """Fetches the previous tier's art generation metadata for visual evolution continuity.

    Reads the reward_hdr_guid from session state (populated during WebSocket/REST handshake),
    then queries the reward_line table for the highest tier entry to retrieve the art prompt
    and tier level used in the previous generation.

    Args:
        tool_context: ADK ToolContext (auto-injected) for session state access.

    Returns:
        dict with status, previous_prompt, and previous_tier.
    """
    from service.reward.app_mm_reward_line_service import AppMmRewardLineService
    from service.reward.app_mm_reward_hdr_service import AppMmRewardHdrService

    try:
        # Get library_hdr_guid from session state to find the reward_hdr
        library_hdr_guid = tool_context.state.get("library_hdr_guid")
        user_guid = tool_context.state.get("user_guid")

        if not library_hdr_guid:
            return {
                "status": "error",
                "message": "No library_hdr_guid found in session state.",
            }

        # Find the reward_hdr for this library
        from util.supabase_config import supabase

        reward_hdr_response = (
            supabase.table(AppMmRewardHdrService.TABLE_NAME)
            .select("guid")
            .eq("llibrary_hdr_guid", str(library_hdr_guid))
            .order("tier_level", desc=True)
            .limit(1)
            .execute()
        )

        if not reward_hdr_response.data:
            return {
                "status": "error",
                "message": "No reward header found for this library.",
            }

        reward_hdr_guid = reward_hdr_response.data[0]["guid"]

        # Get the highest tier reward line
        latest_reward_line = AppMmRewardLineService.get_highest_tier_by_reward_hdr(reward_hdr_guid)

        if not latest_reward_line:
            return {
                "status": "error",
                "message": "No previous reward line found. This may be the first generation.",
            }

        return {
            "status": "success",
            "previous_prompt": latest_reward_line.art_prompt or "No prompt recorded for previous tier.",
            "previous_tier": latest_reward_line.tier_level or 0,
            "previous_image_url": latest_reward_line.image_url,
        }

    except Exception as e:
        logger.error(f"Error fetching previous art metadata: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to fetch previous art metadata: {str(e)}",
        }
