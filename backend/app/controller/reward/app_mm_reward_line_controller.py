from fastapi import APIRouter, status
from uuid import UUID
from typing import List
from model.reward.app_mm_reward_line import AppMmRewardLineCreate, AppMmRewardLineUpdate, AppMmRewardLineResponse
from service.reward.app_mm_reward_line_service import AppMmRewardLineService
from model.api_response import ApiResponse

router = APIRouter(prefix="/reward-lines", tags=["reward-lines"])


@router.post("/create", response_model=ApiResponse[AppMmRewardLineResponse], status_code=status.HTTP_201_CREATED)
def create_reward_line(reward_line: AppMmRewardLineCreate):
    """Create a new reward line"""
    try:
        result = AppMmRewardLineService.create_reward_line(reward_line)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})


@router.get("/get-by-guid/{reward_line_id}", response_model=ApiResponse[AppMmRewardLineResponse])
def get_reward_line(reward_line_id: UUID):
    """Get reward line by ID"""
    reward_line = AppMmRewardLineService.get_reward_line_by_id(reward_line_id)
    if not reward_line:
        return ApiResponse.error({"message": "Reward line not found"})
    return ApiResponse.success(reward_line)


@router.get("/get-all", response_model=ApiResponse[List[AppMmRewardLineResponse]])
def get_all_reward_lines():
    """Get all reward lines"""
    reward_lines = AppMmRewardLineService.get_all_reward_lines()
    return ApiResponse.success(reward_lines)


@router.get("/get-by-user/{user_guid}", response_model=ApiResponse[List[AppMmRewardLineResponse]])
def get_reward_lines_by_user(user_guid: UUID):
    """Get all reward lines for a specific user"""
    reward_lines = AppMmRewardLineService.get_reward_lines_by_user(user_guid)
    return ApiResponse.success(reward_lines)


@router.get("/get-by-reward-hdr/{reward_hdr_guid}", response_model=ApiResponse[List[AppMmRewardLineResponse]])
def get_reward_lines_by_reward_hdr(reward_hdr_guid: UUID):
    """Get all reward lines for a specific reward header"""
    reward_lines = AppMmRewardLineService.get_reward_lines_by_reward_hdr(reward_hdr_guid)
    return ApiResponse.success(reward_lines)

@router.get("/get-highest-tier/{reward_hdr_guid}", response_model=ApiResponse[AppMmRewardLineResponse])
def get_highest_tier_by_reward_hdr(reward_hdr_guid: UUID):
    """Get the reward line with the highest tier_level for a specific reward header"""
    reward_line = AppMmRewardLineService.get_highest_tier_by_reward_hdr(reward_hdr_guid)
    if not reward_line:
        return ApiResponse.error({"message": "No reward lines found for this reward header"})
    return ApiResponse.success(reward_line)


@router.put("/update/{reward_line_id}", response_model=ApiResponse[AppMmRewardLineResponse])
def update_reward_line(reward_line_id: UUID, reward_line: AppMmRewardLineUpdate):
    """Update reward line by ID"""
    updated_reward_line = AppMmRewardLineService.update_reward_line(reward_line_id, reward_line)
    if not updated_reward_line:
        return ApiResponse.error({"message": "Reward line not found"})
    return ApiResponse.success(updated_reward_line)


@router.delete("/delete-by-guid/{reward_line_id}", response_model=ApiResponse[dict])
def delete_reward_line(reward_line_id: UUID):
    """Delete reward line by ID"""
    success = AppMmRewardLineService.delete_reward_line(reward_line_id)
    if not success:
        return ApiResponse.error({"message": "Reward line not found"})
    return ApiResponse.success({"message": "Reward line deleted successfully"})


@router.post("/generate-test-data", response_model=ApiResponse[AppMmRewardLineResponse], status_code=status.HTTP_201_CREATED)
def generate_test_reward_line():
    """Generate a test reward line with pre-configured GUIDs and image URL."""
    try:
        test_data = AppMmRewardLineCreate(
            user_guid=UUID("69cdaaa7-9800-42d9-a4c4-23db3b685a2d"),
            reward_hdr_guid=UUID("b4304e95-34b4-4650-904f-32072a3edde1"),
            image_url="https://rebzcnrqkaqjbtaiwggw.supabase.co/storage/v1/object/public/file_upload_bucket/reward_art_image_dir/legacy_art_2c6fa4d1.png",
            tier_level=1,
            art_prompt="Design a 2D, flat-style achievement emblem, a 'Seal of Deep Focus', encased within a soft, ornamental circular border. This border should feature elegant, minimalist scholarly or botanical patterns. The central image will be a simple, stylized human silhouette, rendered with fine-liner ink, either seated peacefully, deeply engrossed in a book, or thoughtfully writing at a desk, illustrating profound concentration. The overall aesthetic must be a whimsical, hand-drawn illustration, reminiscent of a cozy, boutique bookshop, utilizing delicate watercolor textures. Employ a warm and inviting color palette dominated by honey gold, soft terracotta, and serene sage green, emphasizing the tranquil activity of focused study and the beautifully understated ornamental containment.",
        )
        result = AppMmRewardLineService.create_reward_line(test_data)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})
