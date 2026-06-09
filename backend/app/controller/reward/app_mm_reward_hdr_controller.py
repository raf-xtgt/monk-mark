from fastapi import APIRouter, status
from uuid import UUID
from typing import List
from model.reward.app_mm_reward_hdr import AppMmRewardHdrCreate, AppMmRewardHdrUpdate, AppMmRewardHdrResponse
from model.reward.app_mm_reward_line import AppMmRewardLineCreate
from model.dto.reward_output_dto import RewardOutputDto, MilestoneEvaluation
from model.dto.reward_simulation_dto import RewardSimulationDto
from service.reward.app_mm_reward_hdr_service import AppMmRewardHdrService
from service.reward.app_mm_reward_line_service import AppMmRewardLineService
from service.agent_trigger.agent_trigger_service import AgentTriggerService
from model.api_response import ApiResponse

router = APIRouter(prefix="/reward-hdrs", tags=["reward-hdrs"])


@router.post("/create", response_model=ApiResponse[AppMmRewardHdrResponse], status_code=status.HTTP_201_CREATED)
def create_reward_hdr(reward: AppMmRewardHdrCreate):
    """Create a new reward header"""
    try:
        result = AppMmRewardHdrService.create_reward_hdr(reward)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})


@router.get("/get-by-guid/{reward_id}", response_model=ApiResponse[AppMmRewardHdrResponse])
def get_reward_hdr(reward_id: UUID):
    """Get reward header by ID"""
    reward = AppMmRewardHdrService.get_reward_hdr_by_id(reward_id)
    if not reward:
        return ApiResponse.error({"message": "Reward header not found"})
    return ApiResponse.success(reward)


@router.get("/get-all", response_model=ApiResponse[List[AppMmRewardHdrResponse]])
def get_all_reward_hdrs():
    """Get all reward headers"""
    rewards = AppMmRewardHdrService.get_all_reward_hdrs()
    return ApiResponse.success(rewards)


@router.get("/get-by-user/{user_guid}", response_model=ApiResponse[List[AppMmRewardHdrResponse]])
def get_reward_hdrs_by_user(user_guid: UUID):
    """Get all reward headers for a specific user"""
    rewards = AppMmRewardHdrService.get_reward_hdrs_by_user(user_guid)
    return ApiResponse.success(rewards)


@router.get("/get-by-notebook/{notebook_hdr_guid}", response_model=ApiResponse[List[AppMmRewardHdrResponse]])
def get_reward_hdrs_by_notebook(notebook_hdr_guid: UUID):
    """Get all reward headers for a specific notebook"""
    rewards = AppMmRewardHdrService.get_reward_hdrs_by_notebook(notebook_hdr_guid)
    return ApiResponse.success(rewards)


@router.put("/update/{reward_id}", response_model=ApiResponse[AppMmRewardHdrResponse])
def update_reward_hdr(reward_id: UUID, reward: AppMmRewardHdrUpdate):
    """Update reward header by ID"""
    updated_reward = AppMmRewardHdrService.update_reward_hdr(reward_id, reward)
    if not updated_reward:
        return ApiResponse.error({"message": "Reward header not found"})
    return ApiResponse.success(updated_reward)


@router.delete("/delete-by-guid/{reward_id}", response_model=ApiResponse[dict])
def delete_reward_hdr(reward_id: UUID):
    """Delete reward header by ID"""
    success = AppMmRewardHdrService.delete_reward_hdr(reward_id)
    if not success:
        return ApiResponse.error({"message": "Reward header not found"})
    return ApiResponse.success({"message": "Reward header deleted successfully"})


@router.get("/get-summary-by-library/{user_guid}/{library_hdr_guid}", response_model=ApiResponse[RewardOutputDto])
def get_reward_summary_by_library(user_guid: UUID, library_hdr_guid: UUID):
    """Get reward summary for a library: rewards list, total focused hours, and total notes"""
    try:
        result = AppMmRewardHdrService.get_reward_summary_by_library(user_guid, library_hdr_guid)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})


@router.post("/evaluate-milestone", response_model=ApiResponse[RewardOutputDto])
def evaluate_reward_milestone(payload: RewardOutputDto):
    """Evaluate milestone progression and persist the evaluation to the reward_hdr record.

    - If reward_list is empty: tier_level = 0, creates a new reward_hdr record with the evaluation in reward_metadata.
    - If reward_list is not empty: retrieves the record with the highest tier_level, updates its reward_metadata.
    - Returns the RewardOutputDto with the milestone_evaluation field populated.
    """
    try:
        # Determine tier_level
        if not payload.reward_list:
            tier_level = 0
        else:
            tier_level = max(
                (r.tier_level for r in payload.reward_list if r.tier_level is not None),
                default=0,
            )

        # Evaluate milestone progression
        evaluation = AppMmRewardHdrService.evaluate_milestone_progression(
            tier_level=tier_level,
            total_focus_hours=payload.total_focused_hrs,
            total_notes_taken=payload.total_notes,
        )

        evaluation_dict = evaluation.model_dump()

        if not payload.reward_list:
            # Create a new reward_hdr record with the evaluation stored in reward_metadata
            create_data = AppMmRewardHdrCreate(
                user_guid=payload.user_guid,
                library_hdr_guid=payload.library_hdr_guid,
                notebook_hdr_guid=payload.library_hdr_guid,  # Use library_hdr_guid as placeholder
                tier_level=tier_level,
                reward_metadata=evaluation_dict,
            )
            new_reward = AppMmRewardHdrService.create_reward_hdr(create_data)
            payload.reward_list = [new_reward]
        else:
            # Find the reward_hdr with the highest tier_level
            highest_reward = max(
                payload.reward_list,
                key=lambda r: r.tier_level if r.tier_level is not None else 0,
            )

            # Update its reward_metadata with the evaluation
            update_data = AppMmRewardHdrUpdate(
                reward_metadata=evaluation_dict,
                tier_level=evaluation.current_tier,
            )
            updated_reward = AppMmRewardHdrService.update_reward_hdr(highest_reward.guid, update_data)

            if updated_reward:
                # Replace the record in the list with the updated one
                payload.reward_list = [
                    updated_reward if r.guid == highest_reward.guid else r
                    for r in payload.reward_list
                ]

        # Attach the milestone evaluation to the response
        payload.milestone_evaluation = evaluation

        return ApiResponse.success(payload)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})


@router.post("/generate-test-data", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED)
def generate_monk_mode_test_data(tier_level: int = 0, progress_type: str = "HALF"):
    """Generate test data for monk mode milestone testing.

    Creates focus sessions and notebook contents to simulate progression.

    Query params:
    - tier_level: The current tier already achieved (0-4). Default: 0.
    - progress_type: 'HALF' for 50% progress toward next tier, 'FULL' for 100%. Default: 'HALF'.
    """
    try:
        if progress_type not in ("HALF", "FULL"):
            return ApiResponse.error({"message": "progress_type must be 'HALF' or 'FULL'"})
        if tier_level < 0 or tier_level > 4:
            return ApiResponse.error({"message": "tier_level must be between 0 and 4"})

        result = AppMmRewardHdrService.generate_test_data(tier_level, progress_type)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})


@router.post("/simulate-rewards", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED)
async def simulate_rewards(payload: RewardSimulationDto):
    """Simulate the full reward flow end-to-end.

    Creates notebook/notes/focus sessions, evaluates milestone progression,
    triggers the appropriate art generation agent if milestone is fulfilled,
    and persists the reward_hdr and reward_line records.

    Input: RewardSimulationDto with user_guid, library_guid, tier_level, progress_type.
    """
    try:
        # Step 1-4: Generate test data and evaluate
        sim_result = AppMmRewardHdrService.simulate_reward_flow(
            user_guid=payload.user_guid,
            library_hdr_guid=payload.library_guid,
            tier_level=payload.tier_level,
            progress_type=payload.progress_type,
        )

        evaluation = sim_result["evaluation"]
        agent_to_trigger = evaluation["agent_to_trigger"]
        notebook_hdr_guid = sim_result["notebook_hdr_guid"]

        # Step 5: Trigger agent if milestone unlocked
        agent_result = None
        reward_hdr_created = None
        reward_line_created = None

        if agent_to_trigger in ("ART_GEN", "ART_EVOLUTION"):
            event_type = "generate_art_evolution" if agent_to_trigger == "ART_EVOLUTION" else "generate_art"

            trigger_result = await AgentTriggerService.trigger_agent(
                user_guid=payload.user_guid,
                library_hdr_guid=payload.library_guid,
                notebook_hdr_guid=UUID(notebook_hdr_guid) if isinstance(notebook_hdr_guid, str) else notebook_hdr_guid,
                event_type=event_type,
            )

            agent_result = {
                "session_id": trigger_result.session_id,
                "responses": trigger_result.responses,
                "storage_url": trigger_result.storage_url,
                "visual_metaphor_prompt": trigger_result.visual_metaphor_prompt,
            }

            # Determine art_prompt
            art_prompt = None
            if trigger_result.visual_metaphor_prompt:
                art_prompt = trigger_result.visual_metaphor_prompt
            elif len(trigger_result.responses) > 1:
                art_prompt = trigger_result.responses[1]

            if agent_to_trigger == "ART_EVOLUTION":
                # Art evolution: add reward_line under the existing reward_hdr
                # Find the existing reward_hdr with the highest tier_level for this library
                existing_rewards = AppMmRewardHdrService.get_reward_hdrs_by_user(payload.user_guid)
                matching_rewards = [
                    r for r in existing_rewards
                    if str(r.library_hdr_guid) == str(payload.library_guid)
                ]

                if matching_rewards:
                    # Use the reward_hdr with the highest tier_level
                    existing_hdr = max(
                        matching_rewards,
                        key=lambda r: r.tier_level if r.tier_level is not None else 0,
                    )

                    # Update the existing reward_hdr tier_level
                    update_data = AppMmRewardHdrUpdate(
                        tier_level=evaluation["current_tier"],
                        image_url=trigger_result.storage_url,
                    )
                    updated_hdr = AppMmRewardHdrService.update_reward_hdr(existing_hdr.guid, update_data)
                    reward_hdr_created = (updated_hdr or existing_hdr).model_dump()

                    # Create reward_line under the existing reward_hdr
                    reward_line_data = AppMmRewardLineCreate(
                        user_guid=payload.user_guid,
                        reward_hdr_guid=existing_hdr.guid,
                        image_url=trigger_result.storage_url,
                        tier_level=evaluation["current_tier"],
                        art_prompt=art_prompt,
                    )
                    reward_line = AppMmRewardLineService.create_reward_line(reward_line_data)
                    reward_line_created = reward_line.model_dump()
                else:
                    # Fallback: no existing reward_hdr found, create a new one
                    reward_hdr_data = AppMmRewardHdrCreate(
                        user_guid=payload.user_guid,
                        library_hdr_guid=payload.library_guid,
                        notebook_hdr_guid=UUID(notebook_hdr_guid) if isinstance(notebook_hdr_guid, str) else notebook_hdr_guid,
                        image_url=trigger_result.storage_url,
                        tier_level=evaluation["current_tier"],
                        reward_metadata=evaluation,
                    )
                    reward_hdr = AppMmRewardHdrService.create_reward_hdr(reward_hdr_data)
                    reward_hdr_created = reward_hdr.model_dump()

                    reward_line_data = AppMmRewardLineCreate(
                        user_guid=payload.user_guid,
                        reward_hdr_guid=reward_hdr.guid,
                        image_url=trigger_result.storage_url,
                        tier_level=evaluation["current_tier"],
                        art_prompt=art_prompt,
                    )
                    reward_line = AppMmRewardLineService.create_reward_line(reward_line_data)
                    reward_line_created = reward_line.model_dump()
            else:
                # ART_GEN: first-time art generation, create a new reward_hdr
                reward_hdr_data = AppMmRewardHdrCreate(
                    user_guid=payload.user_guid,
                    library_hdr_guid=payload.library_guid,
                    notebook_hdr_guid=UUID(notebook_hdr_guid) if isinstance(notebook_hdr_guid, str) else notebook_hdr_guid,
                    image_url=trigger_result.storage_url,
                    tier_level=evaluation["current_tier"],
                    reward_metadata=evaluation,
                )
                reward_hdr = AppMmRewardHdrService.create_reward_hdr(reward_hdr_data)
                reward_hdr_created = reward_hdr.model_dump()

                reward_line_data = AppMmRewardLineCreate(
                    user_guid=payload.user_guid,
                    reward_hdr_guid=reward_hdr.guid,
                    image_url=trigger_result.storage_url,
                    tier_level=evaluation["current_tier"],
                    art_prompt=art_prompt,
                )
                reward_line = AppMmRewardLineService.create_reward_line(reward_line_data)
                reward_line_created = reward_line.model_dump()

        return ApiResponse.success({
            "simulation": sim_result,
            "agent_result": agent_result,
            "reward_hdr_created": reward_hdr_created,
            "reward_line_created": reward_line_created,
        })
    except Exception as e:
        return ApiResponse.error({"message": str(e)})