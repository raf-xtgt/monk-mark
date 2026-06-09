from fastapi import APIRouter, status
from uuid import UUID
from typing import List
from model.gitlab_sync_log.app_mm_gitlab_sync_log import (
    AppMmGitlabSyncLogCreate,
    AppMmGitlabSyncLogUpdate,
    AppMmGitlabSyncLogResponse,
)
from model.dto.gitlab_agent_context_dto import GitlabContextRequest
from service.gitlab_sync_log.app_mm_gitlab_sync_log_service import AppMmGitlabSyncLogService
from model.api_response import ApiResponse

router = APIRouter(prefix="/gitlab-sync-logs", tags=["gitlab-sync-logs"])


@router.post("/create", response_model=ApiResponse[AppMmGitlabSyncLogResponse], status_code=status.HTTP_201_CREATED)
def create_sync_log(data: AppMmGitlabSyncLogCreate):
    """Create a new gitlab sync log entry"""
    try:
        result = AppMmGitlabSyncLogService.create_sync_log(data)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})


@router.get("/get-by-guid/{guid}", response_model=ApiResponse[AppMmGitlabSyncLogResponse])
def get_sync_log(guid: UUID):
    """Get sync log by GUID"""
    sync_log = AppMmGitlabSyncLogService.get_sync_log_by_id(guid)
    if not sync_log:
        return ApiResponse.error({"message": "Gitlab sync log not found"})
    return ApiResponse.success(sync_log)


@router.get("/get-all", response_model=ApiResponse[List[AppMmGitlabSyncLogResponse]])
def get_all_sync_logs():
    """Get all sync logs"""
    sync_logs = AppMmGitlabSyncLogService.get_all_sync_logs()
    return ApiResponse.success(sync_logs)


@router.get("/get-by-user/{user_guid}", response_model=ApiResponse[List[AppMmGitlabSyncLogResponse]])
def get_sync_logs_by_user(user_guid: UUID):
    """Get all sync logs for a specific user"""
    sync_logs = AppMmGitlabSyncLogService.get_sync_logs_by_user(user_guid)
    return ApiResponse.success(sync_logs)


@router.put("/update/{guid}", response_model=ApiResponse[AppMmGitlabSyncLogResponse])
def update_sync_log(guid: UUID, data: AppMmGitlabSyncLogUpdate):
    """Update sync log by GUID"""
    updated = AppMmGitlabSyncLogService.update_sync_log(guid, data)
    if not updated:
        return ApiResponse.error({"message": "Gitlab sync log not found"})
    return ApiResponse.success(updated)


@router.delete("/delete-by-guid/{guid}", response_model=ApiResponse[dict])
def delete_sync_log(guid: UUID):
    """Delete sync log by GUID"""
    success = AppMmGitlabSyncLogService.delete_sync_log(guid)
    if not success:
        return ApiResponse.error({"message": "Gitlab sync log not found"})
    return ApiResponse.success({"message": "Gitlab sync log deleted successfully"})


@router.post("/context", response_model=ApiResponse[dict])
def get_gitlab_context(request: GitlabContextRequest):
    """Retrieve the assembled gitlab agent context for a user's reading data.

    Combines book metadata, notebook content (text + file links), and chat transcripts
    into a structured GitlabAgentContextDto.
    """
    from service.agents.tools.gitlab_tools import build_gitlab_context

    result = build_gitlab_context(
        user_guid=str(request.user_guid),
        library_hdr_guid=str(request.library_hdr_guid) if request.library_hdr_guid else None,
        notebook_hdr_guid=str(request.notebook_hdr_guid) if request.notebook_hdr_guid else None,
        llm_chat_hdr_guid=str(request.llm_chat_hdr_guid) if request.llm_chat_hdr_guid else None,
    )

    if result.get("status") == "error":
        return ApiResponse.error({"message": result.get("message", "Unknown error")})

    return ApiResponse.success(result)