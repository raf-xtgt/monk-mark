from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from model.reward.app_mm_reward_line import AppMmRewardLineResponse


class DashboardStatsResponseDto(BaseModel):
    user_guid: UUID
    total_focused_hrs: float
    total_notes: int


class DashboardNotebookResponseDto(BaseModel):
    notebook_hdr_guid: UUID
    library_hdr_guid: UUID
    notebook_name: str
    total_notes: int
    last_updated: Optional[datetime] = None


class DashboardLegacyArtResponseDto(BaseModel):
    reward_hdr_guid: UUID
    reward_line_guid: UUID
    reward_line_image_url: str
    tier_level: Optional[int] = None
    notebook_hdr_guid: UUID
    library_hdr_guid: UUID
    notebook_name: str


class DashboardLegacyArtByHdrResponseDto(BaseModel):
    reward_hdr_guid: UUID
    reward_hdr_tier_level: Optional[int] = None
    reward_hdr_library_guid: UUID
    reward_hdr_notebook_guid: UUID
    reward_lines: List[AppMmRewardLineResponse] = []