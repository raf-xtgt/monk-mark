from fastapi import APIRouter, status
from uuid import UUID
from typing import List
from model.dto.dashboard_dto import DashboardStatsResponseDto, DashboardNotebookResponseDto, DashboardLegacyArtResponseDto
from service.dashboard.dashboard_service import DashboardService
from model.api_response import ApiResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats/{user_guid}", response_model=ApiResponse)
def get_user_stats(user_guid: UUID):
    """Get total focus hours and total notes for a user across all books."""
    try:
        result = DashboardService.get_user_stats(user_guid)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})


@router.get("/notebooks/{user_guid}", response_model=ApiResponse)
def get_user_notebooks(user_guid: UUID):
    """Get all notebooks for a user with note count and last updated date."""
    try:
        result = DashboardService.get_user_notebooks(user_guid)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})


@router.get("/legacy-arts/{user_guid}", response_model=ApiResponse)
def get_user_legacy_arts(user_guid: UUID):
    """Get all legacy art reward lines for a user with notebook context."""
    try:
        result = DashboardService.get_user_legacy_arts(user_guid)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})


@router.get("/legacy-arts-by-hdr/{user_guid}", response_model=ApiResponse)
def get_user_legacy_arts_by_hdr(user_guid: UUID):
    """Get legacy arts grouped by reward_hdr for a user."""
    try:
        result = DashboardService.get_user_legacy_arts_by_hdr(user_guid)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})
