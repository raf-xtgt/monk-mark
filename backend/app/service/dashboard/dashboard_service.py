from uuid import UUID
from typing import List
from util.supabase_config import supabase
from model.dto.dashboard_dto import DashboardStatsResponseDto, DashboardNotebookResponseDto, DashboardLegacyArtResponseDto, DashboardLegacyArtByHdrResponseDto
from model.reward.app_mm_reward_line import AppMmRewardLineResponse


class DashboardService:
    FOCUS_SESSION_TABLE = "app_mm_focus_session"
    NOTEBOOK_HDR_TABLE = "app_mm_notebook_hdr"
    NOTEBOOK_CONTENT_TABLE = "app_mm_notebook_content"

    @staticmethod
    def get_user_stats(user_guid: UUID) -> DashboardStatsResponseDto:
        """Get total focus hours and total notes for a user across all books."""

        # 1. Sum focus session hours
        focus_response = supabase.table(DashboardService.FOCUS_SESSION_TABLE).select(
            "time_hrs, time_seconds"
        ).eq("user_guid", str(user_guid)).execute()

        total_hrs = 0.0
        total_seconds = 0
        for session in focus_response.data:
            if session.get("time_hrs"):
                try:
                    total_hrs += float(session["time_hrs"])
                except (ValueError, TypeError):
                    pass
            if session.get("time_seconds"):
                total_seconds += int(session["time_seconds"])

        total_focused_hrs = total_hrs + (total_seconds / 3600.0)

        # 2. Count total notebook contents
        content_response = supabase.table(DashboardService.NOTEBOOK_CONTENT_TABLE).select(
            "*", count="exact"
        ).eq("user_guid", str(user_guid)).execute()

        total_notes = content_response.count if content_response.count is not None else 0

        return DashboardStatsResponseDto(
            user_guid=user_guid,
            total_focused_hrs=round(total_focused_hrs, 2),
            total_notes=total_notes,
        )

    @staticmethod
    def get_user_notebooks(user_guid: UUID) -> List[DashboardNotebookResponseDto]:
        """Get all notebooks for a user with note count and last updated date."""

        # 1. Get all notebook headers for the user
        notebooks_response = supabase.table(DashboardService.NOTEBOOK_HDR_TABLE).select(
            "guid, library_hdr_guid, name"
        ).eq("user_guid", str(user_guid)).execute()

        if not notebooks_response.data:
            return []

        results: List[DashboardNotebookResponseDto] = []

        for notebook in notebooks_response.data:
            notebook_guid = notebook["guid"]

            # 2. Count notes for this notebook
            count_response = supabase.table(DashboardService.NOTEBOOK_CONTENT_TABLE).select(
                "*", count="exact"
            ).eq("notebook_hdr_guid", str(notebook_guid)).execute()

            total_notes = count_response.count if count_response.count is not None else 0

            # 3. Get the most recently updated content for last_updated
            latest_response = supabase.table(DashboardService.NOTEBOOK_CONTENT_TABLE).select(
                "updated_date"
            ).eq("notebook_hdr_guid", str(notebook_guid)).order(
                "updated_date", desc=True
            ).limit(1).execute()

            last_updated = None
            if latest_response.data:
                last_updated = latest_response.data[0].get("updated_date")

            results.append(DashboardNotebookResponseDto(
                notebook_hdr_guid=notebook_guid,
                library_hdr_guid=notebook["library_hdr_guid"],
                notebook_name=notebook["name"],
                total_notes=total_notes,
                last_updated=last_updated,
            ))

        return results

    REWARD_HDR_TABLE = "app_mm_reward_hdr"
    REWARD_LINE_TABLE = "app_mm_reward_line"

    @staticmethod
    def get_user_legacy_arts(user_guid: UUID) -> List[DashboardLegacyArtResponseDto]:
        """Get all legacy art reward lines for a user with notebook context."""

        # 1. Get all reward lines for this user that have an image_url
        reward_lines_response = supabase.table(DashboardService.REWARD_LINE_TABLE).select(
            "guid, reward_hdr_guid, image_url, tier_level"
        ).eq("user_guid", str(user_guid)).filter("image_url", "not.is", "null").execute()

        if not reward_lines_response.data:
            return []

        # 2. Get all reward_hdr guids to fetch their notebook/library context
        reward_hdr_guids = list({rl["reward_hdr_guid"] for rl in reward_lines_response.data})

        reward_hdrs_response = supabase.table(DashboardService.REWARD_HDR_TABLE).select(
            "guid, notebook_hdr_guid, llibrary_hdr_guid"
        ).in_("guid", reward_hdr_guids).execute()

        # Build a map: reward_hdr_guid -> {notebook_hdr_guid, library_hdr_guid}
        hdr_map = {}
        for hdr in reward_hdrs_response.data:
            hdr_map[hdr["guid"]] = {
                "notebook_hdr_guid": hdr["notebook_hdr_guid"],
                "library_hdr_guid": hdr.get("llibrary_hdr_guid"),
            }

        # 3. Get notebook names for all relevant notebook_hdr_guids
        notebook_guids = list({
            v["notebook_hdr_guid"] for v in hdr_map.values() if v["notebook_hdr_guid"]
        })

        notebook_name_map = {}
        if notebook_guids:
            notebooks_response = supabase.table(DashboardService.NOTEBOOK_HDR_TABLE).select(
                "guid, name"
            ).in_("guid", notebook_guids).execute()

            for nb in notebooks_response.data:
                notebook_name_map[nb["guid"]] = nb["name"]

        # 4. Assemble the flat list
        results: List[DashboardLegacyArtResponseDto] = []
        for rl in reward_lines_response.data:
            hdr_context = hdr_map.get(rl["reward_hdr_guid"], {})
            notebook_hdr_guid = hdr_context.get("notebook_hdr_guid")
            library_hdr_guid = hdr_context.get("library_hdr_guid")
            notebook_name = notebook_name_map.get(notebook_hdr_guid, "Unknown Notebook") if notebook_hdr_guid else "Unknown Notebook"

            results.append(DashboardLegacyArtResponseDto(
                reward_hdr_guid=rl["reward_hdr_guid"],
                reward_line_guid=rl["guid"],
                reward_line_image_url=rl["image_url"],
                tier_level=rl.get("tier_level"),
                notebook_hdr_guid=notebook_hdr_guid or "00000000-0000-0000-0000-000000000000",
                library_hdr_guid=library_hdr_guid or "00000000-0000-0000-0000-000000000000",
                notebook_name=notebook_name,
            ))

        return results

    @staticmethod
    def get_user_legacy_arts_by_hdr(user_guid: UUID) -> List[DashboardLegacyArtByHdrResponseDto]:
        """Get legacy arts grouped by reward_hdr for a user."""

        # 1. Get all reward_hdrs for this user
        reward_hdrs_response = supabase.table(DashboardService.REWARD_HDR_TABLE).select(
            "guid, tier_level, llibrary_hdr_guid, notebook_hdr_guid"
        ).eq("user_guid", str(user_guid)).order("tier_level", desc=True).execute()

        if not reward_hdrs_response.data:
            return []

        # 2. Get all reward_lines for this user
        reward_lines_response = supabase.table(DashboardService.REWARD_LINE_TABLE).select(
            "*"
        ).eq("user_guid", str(user_guid)).execute()

        # Group reward_lines by reward_hdr_guid
        lines_by_hdr: dict = {}
        for rl in reward_lines_response.data:
            hdr_guid = rl["reward_hdr_guid"]
            if hdr_guid not in lines_by_hdr:
                lines_by_hdr[hdr_guid] = []
            lines_by_hdr[hdr_guid].append(AppMmRewardLineResponse(**rl))

        # 3. Assemble grouped response
        results: List[DashboardLegacyArtByHdrResponseDto] = []
        for hdr in reward_hdrs_response.data:
            hdr_guid = hdr["guid"]
            results.append(DashboardLegacyArtByHdrResponseDto(
                reward_hdr_guid=hdr_guid,
                reward_hdr_tier_level=hdr.get("tier_level"),
                reward_hdr_library_guid=hdr.get("llibrary_hdr_guid") or "00000000-0000-0000-0000-000000000000",
                reward_hdr_notebook_guid=hdr.get("notebook_hdr_guid") or "00000000-0000-0000-0000-000000000000",
                reward_lines=lines_by_hdr.get(hdr_guid, []),
            ))

        return results
