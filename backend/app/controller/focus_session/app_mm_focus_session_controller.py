from fastapi import APIRouter, status
from uuid import UUID
from typing import List
from model.focus_session.app_mm_focus_session import (
    AppMmFocusSessionCreate,
    AppMmFocusSessionUpdate,
    AppMmFocusSessionResponse
)
from service.focus_session.app_mm_focus_session_service import AppMmFocusSessionService
from model.api_response import ApiResponse
from model.dto.focus_session_query_criteria import FocusSessionQueryCriteria

router = APIRouter(prefix="/focus-sessions", tags=["focus-sessions"])

@router.post("/create", response_model=ApiResponse[AppMmFocusSessionResponse], status_code=status.HTTP_201_CREATED)
def create_focus_session(focus_session: AppMmFocusSessionCreate):
    """Create a new focus session"""
    try:
        result = AppMmFocusSessionService.create_focus_session(focus_session)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})

@router.get("/get-by-guid/{focus_session_id}", response_model=ApiResponse[AppMmFocusSessionResponse])
def get_focus_session(focus_session_id: UUID):
    """Get focus session by ID"""
    focus_session = AppMmFocusSessionService.get_focus_session_by_id(focus_session_id)
    if not focus_session:
        return ApiResponse.error({"message": "Focus session not found"})
    return ApiResponse.success(focus_session)

@router.get("/get-all", response_model=ApiResponse[List[AppMmFocusSessionResponse]])
def get_all_focus_sessions():
    """Get all focus sessions"""
    focus_sessions = AppMmFocusSessionService.get_all_focus_sessions()
    return ApiResponse.success(focus_sessions)

@router.get("/get-by-user/{user_guid}", response_model=ApiResponse[List[AppMmFocusSessionResponse]])
def get_focus_sessions_by_user(user_guid: UUID):
    """Get all focus sessions for a specific user"""
    focus_sessions = AppMmFocusSessionService.get_focus_sessions_by_user(user_guid)
    return ApiResponse.success(focus_sessions)

@router.get("/get-by-library/{library_hdr_guid}", response_model=ApiResponse[List[AppMmFocusSessionResponse]])
def get_focus_sessions_by_library(library_hdr_guid: UUID):
    """Get all focus sessions for a specific library header"""
    focus_sessions = AppMmFocusSessionService.get_focus_sessions_by_library(library_hdr_guid)
    return ApiResponse.success(focus_sessions)

@router.put("/update/{focus_session_id}", response_model=ApiResponse[AppMmFocusSessionResponse])
def update_focus_session(focus_session_id: UUID, focus_session: AppMmFocusSessionUpdate):
    """Update focus session by ID"""
    updated_focus_session = AppMmFocusSessionService.update_focus_session(focus_session_id, focus_session)
    if not updated_focus_session:
        return ApiResponse.error({"message": "Focus session not found"})
    return ApiResponse.success(updated_focus_session)

@router.delete("/delete-by-guid/{focus_session_id}", response_model=ApiResponse[dict])
def delete_focus_session(focus_session_id: UUID):
    """Delete focus session by ID"""
    success = AppMmFocusSessionService.delete_focus_session(focus_session_id)
    if not success:
        return ApiResponse.error({"message": "Focus session not found"})
    return ApiResponse.success({"message": "Focus session deleted successfully"})

@router.post("/get-by-criteria", response_model=ApiResponse[List[AppMmFocusSessionResponse]], status_code=status.HTTP_201_CREATED)
def get_focus_session_by_criteria(query_criteria: FocusSessionQueryCriteria):
    """Get focus sessions by criteria"""
    try:
        focus_sessions = AppMmFocusSessionService.get_focus_sessions_by_criteria(query_criteria)
        return ApiResponse.success(focus_sessions)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})