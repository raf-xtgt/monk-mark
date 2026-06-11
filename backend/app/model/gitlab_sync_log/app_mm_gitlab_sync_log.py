from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class AppMmGitlabSyncLogCreate(BaseModel):
    user_guid: Optional[UUID] = None
    focus_session_guid: Optional[UUID] = None
    notebook_hdr_guid: Optional[UUID] = None
    library_hdr_guid: Optional[UUID] = None
    llm_chat_hdr_guid: Optional[UUID] = None
    reward_line_guid: Optional[UUID] = None
    branch_name: Optional[str] = None
    issue_url: Optional[str] = None
    merge_request_url: Optional[str] = None
    file_url: Optional[str] = None
    sync_status: Optional[str] = None


class AppMmGitlabSyncLogUpdate(BaseModel):
    user_guid: Optional[UUID] = None
    focus_session_guid: Optional[UUID] = None
    notebook_hdr_guid: Optional[UUID] = None
    library_hdr_guid: Optional[UUID] = None
    llm_chat_hdr_guid: Optional[UUID] = None
    reward_line_guid: Optional[UUID] = None
    branch_name: Optional[str] = None
    issue_url: Optional[str] = None
    merge_request_url: Optional[str] = None
    file_url: Optional[str] = None
    sync_status: Optional[str] = None


class AppMmGitlabSyncLogResponse(BaseModel):
    guid: UUID
    user_guid: Optional[UUID] = None
    focus_session_guid: Optional[UUID] = None
    notebook_hdr_guid: Optional[UUID] = None
    library_hdr_guid: Optional[UUID] = None
    llm_chat_hdr_guid: Optional[UUID] = None
    reward_line_guid: Optional[UUID] = None
    branch_name: Optional[str] = None
    issue_url: Optional[str] = None
    merge_request_url: Optional[str] = None
    file_url: Optional[str] = None
    sync_status: Optional[str] = None
    created_date: datetime
    updated_date: datetime

    class Config:
        from_attributes = True
