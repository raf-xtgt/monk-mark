from uuid import UUID, uuid4
from typing import List, Optional
from util.supabase_config import supabase
from model.reward.app_mm_reward_line import AppMmRewardLineCreate, AppMmRewardLineUpdate, AppMmRewardLineResponse


class AppMmRewardLineService:
    TABLE_NAME = "app_mm_reward_line"

    @staticmethod
    def create_reward_line(reward_line_data: AppMmRewardLineCreate) -> AppMmRewardLineResponse:
        """Create a new reward line"""
        new_reward_line = {
            "guid": str(uuid4()),
            "user_guid": str(reward_line_data.user_guid),
            "reward_hdr_guid": str(reward_line_data.reward_hdr_guid),
            "file_upload_guid": str(reward_line_data.file_upload_guid) if reward_line_data.file_upload_guid else None,
            "image_url": reward_line_data.image_url,
            "tier_level": reward_line_data.tier_level,
            "art_prompt": reward_line_data.art_prompt,
        }

        response = supabase.table(AppMmRewardLineService.TABLE_NAME).insert(new_reward_line).execute()

        if not response.data:
            raise Exception("Failed to create reward line")

        return AppMmRewardLineResponse(**response.data[0])

    @staticmethod
    def get_reward_line_by_id(reward_line_id: UUID) -> Optional[AppMmRewardLineResponse]:
        """Get reward line by GUID"""
        response = supabase.table(AppMmRewardLineService.TABLE_NAME).select("*").eq("guid", str(reward_line_id)).execute()

        if not response.data:
            return None

        return AppMmRewardLineResponse(**response.data[0])

    @staticmethod
    def get_all_reward_lines() -> List[AppMmRewardLineResponse]:
        """Get all reward lines"""
        response = supabase.table(AppMmRewardLineService.TABLE_NAME).select("*").execute()

        return [AppMmRewardLineResponse(**row) for row in response.data]

    @staticmethod
    def get_reward_lines_by_user(user_guid: UUID) -> List[AppMmRewardLineResponse]:
        """Get all reward lines for a specific user"""
        response = supabase.table(AppMmRewardLineService.TABLE_NAME).select("*").eq("user_guid", str(user_guid)).execute()

        return [AppMmRewardLineResponse(**row) for row in response.data]

    @staticmethod
    def get_reward_lines_by_reward_hdr(reward_hdr_guid: UUID) -> List[AppMmRewardLineResponse]:
        """Get all reward lines for a specific reward header"""
        response = supabase.table(AppMmRewardLineService.TABLE_NAME).select("*").eq("reward_hdr_guid", str(reward_hdr_guid)).execute()

        return [AppMmRewardLineResponse(**row) for row in response.data]

    @staticmethod
    def get_highest_tier_by_reward_hdr(reward_hdr_guid: UUID) -> Optional[AppMmRewardLineResponse]:
        """Get the reward line with the highest tier_level for a specific reward header"""
        response = (
            supabase.table(AppMmRewardLineService.TABLE_NAME)
            .select("*")
            .eq("reward_hdr_guid", str(reward_hdr_guid))
            .order("tier_level", desc=True)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return AppMmRewardLineResponse(**response.data[0])

    @staticmethod
    def update_reward_line(reward_line_id: UUID, reward_line_data: AppMmRewardLineUpdate) -> Optional[AppMmRewardLineResponse]:
        """Update reward line by GUID"""
        update_data = reward_line_data.model_dump(exclude_unset=True)

        if not update_data:
            return AppMmRewardLineService.get_reward_line_by_id(reward_line_id)

        # Convert UUIDs to strings for Supabase
        for key in ["user_guid", "reward_hdr_guid", "file_upload_guid"]:
            if key in update_data and update_data[key] is not None:
                update_data[key] = str(update_data[key])

        response = supabase.table(AppMmRewardLineService.TABLE_NAME).update(update_data).eq("guid", str(reward_line_id)).execute()

        if not response.data:
            return None

        return AppMmRewardLineResponse(**response.data[0])

    @staticmethod
    def delete_reward_line(reward_line_id: UUID) -> bool:
        """Delete reward line by GUID"""
        response = supabase.table(AppMmRewardLineService.TABLE_NAME).delete().eq("guid", str(reward_line_id)).execute()

        return len(response.data) > 0
