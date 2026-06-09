from pydantic import BaseModel
from typing import Optional, List, Literal
from uuid import UUID
from model.reward.app_mm_reward_hdr import AppMmRewardHdrResponse


class MilestoneEvaluation(BaseModel):
    current_tier: int
    next_tier: int
    hour_threshold: float
    note_threshold: int
    hour_completion_percentage: float
    note_completion_percentage: float
    note_completion_ratio: str
    is_hour_fulfilled: bool
    is_note_fulfilled: bool
    agent_to_trigger: Literal["ART_GEN", "ART_EVOLUTION", "NO_AGENT"]
    remarks: Optional[str] = None
    remaining_hours: Optional[float] = None
    remaining_notes: Optional[int] = None


class RewardOutputDto(BaseModel):
    user_guid: UUID
    library_hdr_guid: Optional[UUID] = None
    reward_list: List[AppMmRewardHdrResponse] = []
    total_focused_hrs: float
    total_notes: int
    milestone_evaluation: Optional[MilestoneEvaluation] = None
