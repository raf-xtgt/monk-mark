from uuid import UUID, uuid4
from typing import List, Optional
from util.supabase_config import supabase
from model.gitlab_sync_log.app_mm_gitlab_sync_log import (
    AppMmGitlabSyncLogCreate,
    AppMmGitlabSyncLogUpdate,
    AppMmGitlabSyncLogResponse,
)


class AppMmGitlabSyncLogService:
    TABLE_NAME = "app_mm_gitlab_sync_log"

    @staticmethod
    def create_sync_log(data: AppMmGitlabSyncLogCreate) -> AppMmGitlabSyncLogResponse:
        """Create a new gitlab sync log entry"""
        new_record = {
            "guid": str(uuid4()),
            **{k: str(v) if v is not None else None for k, v in data.model_dump().items()},
        }

        response = supabase.table(AppMmGitlabSyncLogService.TABLE_NAME).insert(new_record).execute()

        if not response.data:
            raise Exception("Failed to create gitlab sync log")

        return AppMmGitlabSyncLogResponse(**response.data[0])

    @staticmethod
    def get_sync_log_by_id(guid: UUID) -> Optional[AppMmGitlabSyncLogResponse]:
        """Get sync log by GUID"""
        response = (
            supabase.table(AppMmGitlabSyncLogService.TABLE_NAME)
            .select("*")
            .eq("guid", str(guid))
            .execute()
        )

        if not response.data:
            return None

        return AppMmGitlabSyncLogResponse(**response.data[0])

    @staticmethod
    def get_all_sync_logs() -> List[AppMmGitlabSyncLogResponse]:
        """Get all sync logs"""
        response = supabase.table(AppMmGitlabSyncLogService.TABLE_NAME).select("*").execute()

        return [AppMmGitlabSyncLogResponse(**record) for record in response.data]

    @staticmethod
    def get_sync_logs_by_user(user_guid: UUID) -> List[AppMmGitlabSyncLogResponse]:
        """Get all sync logs for a specific user"""
        response = (
            supabase.table(AppMmGitlabSyncLogService.TABLE_NAME)
            .select("*")
            .eq("user_guid", str(user_guid))
            .order("created_date", desc=True)
            .execute()
        )

        return [AppMmGitlabSyncLogResponse(**record) for record in response.data]

    @staticmethod
    def update_sync_log(guid: UUID, data: AppMmGitlabSyncLogUpdate) -> Optional[AppMmGitlabSyncLogResponse]:
        """Update sync log by GUID"""
        update_data = {
            k: str(v) if v is not None else None
            for k, v in data.model_dump(exclude_unset=True).items()
        }

        if not update_data:
            return AppMmGitlabSyncLogService.get_sync_log_by_id(guid)

        response = (
            supabase.table(AppMmGitlabSyncLogService.TABLE_NAME)
            .update(update_data)
            .eq("guid", str(guid))
            .execute()
        )

        if not response.data:
            return None

        return AppMmGitlabSyncLogResponse(**response.data[0])

    @staticmethod
    def delete_sync_log(guid: UUID) -> bool:
        """Delete sync log by GUID"""
        response = (
            supabase.table(AppMmGitlabSyncLogService.TABLE_NAME)
            .delete()
            .eq("guid", str(guid))
            .execute()
        )

        return len(response.data) > 0

# TODO: Add a method to get the reading context