# backend/app/controller/agent_trigger/agent_trigger_controller.py
# Source: adk-local-docs/docs/runtime/event-loop.md (Runner.run_async pattern)
#
# REST endpoint to trigger AI agents directly via Runner.run_async.
# Delegates execution logic to AgentTriggerService.

import logging
from uuid import UUID
from typing import Optional, List

from fastapi import APIRouter, status
from pydantic import BaseModel

from model.api_response import ApiResponse
from service.agent_trigger.agent_trigger_service import AgentTriggerService
from model.dto.note_taking_dto import NoteTakingAgentRequest, NoteTakingAgentResponse
from model.dto.milestone_quote_dto import MilestoneQuoteRequest, MilestoneQuoteResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["agent-trigger"])


class AgentTriggerRequest(BaseModel):
    """Request payload for triggering an agent."""
    user_guid: UUID
    library_hdr_guid: UUID
    notebook_hdr_guid: UUID
    llm_chat_hdr_guid: Optional[UUID] = None
    event_type: str
    message: Optional[str] = None


class GitlabAgentOutputResponse(BaseModel):
    """Structured output from the gitlab_agent_v2 sequential pipeline."""
    issue_result: Optional[str] = None
    issue_url: Optional[str] = None
    branch_result: Optional[str] = None
    mr_result: Optional[str] = None
    visual_motif_result: Optional[str] = None


class AgentTriggerResponse(BaseModel):
    """Response from an agent trigger invocation."""
    session_id: str
    responses: List[str]
    storage_url: Optional[str] = None
    visual_metaphor_prompt: Optional[str] = None
    gitlab_output: Optional[GitlabAgentOutputResponse] = None


class ArtGenerationAgentTriggerRequest(BaseModel):
    user_guid: UUID
    visual_motif: Optional[str] = None

class ArtEvolutionAgentTriggerRequest(BaseModel):
    user_guid: UUID
    library_hdr_guid: UUID
    visual_motif: Optional[str] = None


@router.post(
    "/trigger-art",
    response_model=ApiResponse[AgentTriggerResponse],
    status_code=status.HTTP_200_OK,
)
async def trigger_art_agent(request: ArtGenerationAgentTriggerRequest):
    """Trigger the art_generator_agent with a visual motif.

    Passes the visual motif as thematic context to the art pipeline which
    generates a visual metaphor prompt and iteratively produces artwork.

    Request payload:
    - user_guid: The user requesting art generation.
    - visual_motif: Optional single-sentence visual theme for the artwork.
    """
    try:
        result = await AgentTriggerService.trigger_art_agent(
            user_guid=request.user_guid,
            visual_motif=request.visual_motif,
        )

        response = AgentTriggerResponse(
            session_id=result.session_id,
            responses=result.responses,
            storage_url=result.storage_url,
            visual_metaphor_prompt=result.visual_metaphor_prompt,
        )
        return ApiResponse.success(response)

    except ValueError as ve:
        return ApiResponse.error({"message": str(ve)})
    except Exception as e:
        logger.error(f"Art agent trigger error: {e}", exc_info=True)
        error_result = AgentTriggerResponse(
            session_id="error",
            responses=[str(e)],
        )
        return ApiResponse.error(error_result)



class ArtEvolutionAgentTriggerRequest(BaseModel):
    user_guid: UUID
    library_hdr_guid: UUID
    visual_motif: Optional[str] = None


@router.post(
    "/trigger-art-evolution",
    response_model=ApiResponse[AgentTriggerResponse],
    status_code=status.HTTP_200_OK,
)
async def trigger_art_evolution_agent(request: ArtEvolutionAgentTriggerRequest):
    """Trigger the art_evolution_agent with the previous artwork and a visual motif.

    Downloads the previous milestone image, then passes it along with the
    visual motif to the art evolution pipeline which preserves structural
    continuity while evolving the composition.

    Request payload:
    - user_guid: The user requesting art evolution.
    - library_hdr_guid: The library (book) to look up previous reward art.
    - visual_motif: Optional single-sentence visual theme for the evolution.
    """
    try:
        result = await AgentTriggerService.trigger_art_evolution_agent(
            user_guid=request.user_guid,
            library_hdr_guid=request.library_hdr_guid,
            visual_motif=request.visual_motif,
        )

        response = AgentTriggerResponse(
            session_id=result.session_id,
            responses=result.responses,
            storage_url=result.storage_url,
            visual_metaphor_prompt=result.visual_metaphor_prompt,
        )
        return ApiResponse.success(response)

    except ValueError as ve:
        return ApiResponse.error({"message": str(ve)})
    except Exception as e:
        logger.error(f"Art evolution agent trigger error: {e}", exc_info=True)
        error_result = AgentTriggerResponse(
            session_id="error",
            responses=[str(e)],
        )
        return ApiResponse.error(error_result)


@router.post(
    "/trigger",
    response_model=ApiResponse[AgentTriggerResponse],
    status_code=status.HTTP_200_OK,
)
async def trigger_agent(request: AgentTriggerRequest):
    """Trigger an AI agent directly using Runner.run_async.

    Creates a session with the required context identifiers in state,
    then invokes the agent pipeline. Routes to the appropriate agent
    based on event_type using the text_runners registry.

    Supported event_types:
    - generate_art
    - generate_art_evolution
    - generate_mantra
    - generate_quiz
    - evaluate_quiz
    - gitlab_doc
    """
    try:
        result = await AgentTriggerService.trigger_agent(
            user_guid=request.user_guid,
            library_hdr_guid=request.library_hdr_guid,
            notebook_hdr_guid=request.notebook_hdr_guid,
            event_type=request.event_type,
            llm_chat_hdr_guid=request.llm_chat_hdr_guid,
            message=request.message,
        )

        response = AgentTriggerResponse(
            session_id=result.session_id,
            responses=result.responses,
            storage_url=result.storage_url,
            visual_metaphor_prompt=result.visual_metaphor_prompt,
            gitlab_output=GitlabAgentOutputResponse(
                issue_result=result.gitlab_output.issue_result,
                issue_url=result.gitlab_output.issue_url,
                branch_result=result.gitlab_output.branch_result,
                mr_result=result.gitlab_output.mr_result,
                visual_motif_result=result.gitlab_output.visual_motif_result,
            ) if result.gitlab_output else None,
        )
        return ApiResponse.success(response)

    except ValueError as ve:
        return ApiResponse.error({"message": str(ve)})
    except Exception as e:
        logger.error(f"Agent trigger error: {e}", exc_info=True)
        error_result = AgentTriggerResponse(
            session_id="error",
            responses=[str(e)],
        )
        return ApiResponse.error(error_result)


@router.post(
    "/trigger-art-generation",
    response_model=ApiResponse[AgentTriggerResponse],
    status_code=status.HTTP_200_OK,
)
async def trigger_art_generation():
    """Convenience endpoint to trigger art generation with pre-configured test GUIDs.

    Uses the hardcoded test data GUIDs for quick testing of the art generator pipeline.
    """
    request = AgentTriggerRequest(
        user_guid=UUID("69cdaaa7-9800-42d9-a4c4-23db3b685a2d"),
        library_hdr_guid=UUID("dede4054-06bb-41b6-bc03-ac74b241160e"),
        notebook_hdr_guid=UUID("f28ede59-922b-4261-9e74-da6ff0d6e480"),
        llm_chat_hdr_guid=UUID("70ad35aa-9216-48e6-b07c-25f85ef29383"),
        event_type="generate_art",
    )
    return await trigger_agent(request)


class GitlabAgentTriggerRequest(BaseModel):
    """Request payload for triggering the gitlab sequential agent."""
    user_guid: UUID
    library_hdr_guid: Optional[UUID] = None
    focus_session_guid: Optional[UUID] = None


@router.post(
    "/trigger-gitlab",
    response_model=ApiResponse[AgentTriggerResponse],
    status_code=status.HTTP_200_OK,
)
async def trigger_gitlab_agent(request: GitlabAgentTriggerRequest):
    """Trigger the GitLab sequential agent pipeline.

    Builds the reading context from the user's data (book metadata, notes,
    transcripts), then passes it to the gitlab_sequential_agent which runs:
    1. Synthesis Agent (generates issue details, markdown notes, MR summary)
    2. Issue Creator (creates GitLab issue)
    3. Developer (creates branch + commits file)
    4. MR Creator (opens merge request)

    Returns the pipeline output including issue, branch, and MR URL.
    """
    try:
        result = await AgentTriggerService.trigger_gitlab_agent(
            user_guid=request.user_guid,
            library_hdr_guid=request.library_hdr_guid,
            focus_session_guid=request.focus_session_guid,
        )

        response = AgentTriggerResponse(
            session_id=result.session_id,
            responses=result.responses,
            storage_url=result.storage_url,
            visual_metaphor_prompt=result.visual_metaphor_prompt,
            gitlab_output=GitlabAgentOutputResponse(
                issue_result=result.gitlab_output.issue_result,
                issue_url=result.gitlab_output.issue_url,
                branch_result=result.gitlab_output.branch_result,
                mr_result=result.gitlab_output.mr_result,
                visual_motif_result=result.gitlab_output.visual_motif_result,
            ) if result.gitlab_output else None,
        )
        return ApiResponse.success(response)

    except ValueError as ve:
        return ApiResponse.error({"message": str(ve)})
    except Exception as e:
        logger.error(f"GitLab agent trigger error: {e}", exc_info=True)
        error_result = AgentTriggerResponse(
            session_id="error",
            responses=[str(e)],
        )
        return ApiResponse.error(error_result)


@router.post(
    "/trigger-note-taking",
    response_model=ApiResponse[NoteTakingAgentResponse],
    status_code=status.HTTP_200_OK,
)
async def trigger_note_taking_agent(request: NoteTakingAgentRequest):
    """Trigger the note-taking agent to generate a concise note from highlighted text.

    Renders the highlight overlay onto the source image, passes the rendered
    image to the note_taking_agent which reads the highlighted passage and
    produces a 15-30 word summary note.

    Request payload:
    - notebook_hdr_guid: The notebook this content belongs to.
    - notebook_content_guid: The specific content entry with the image.
    - image_url: Public URL of the image containing highlighted text.
    - highlight_metadata: {"highlights": [{"x": float, "y": float, "width": float, "height": float}]}
    """
    try:
        result = await AgentTriggerService.trigger_note_taking_agent(
            notebook_hdr_guid=request.notebook_hdr_guid,
            notebook_content_guid=request.notebook_content_guid,
            image_url=request.image_url,
            highlight_metadata=request.highlight_metadata,
        )

        # Extract the generated note from responses
        generated_note = result.responses[0] if result.responses else None

        response = NoteTakingAgentResponse(
            session_id=result.session_id,
            generated_note=generated_note,
            responses=result.responses,
        )
        return ApiResponse.success(response)

    except ValueError as ve:
        return ApiResponse.error({"message": str(ve)})
    except Exception as e:
        logger.error(f"Note taking agent trigger error: {e}", exc_info=True)
        error_result = NoteTakingAgentResponse(
            session_id="error",
            responses=[str(e)],
        )
        return ApiResponse.error(error_result)


@router.post(
    "/trigger-milestone-quote",
    response_model=ApiResponse[MilestoneQuoteResponse],
    status_code=status.HTTP_200_OK,
)
async def trigger_milestone_quote_agent(request: MilestoneQuoteRequest):
    """Trigger the milestone quote agent to generate a motivational phrase.

    Uses the book title and reading progress (current tier, remaining hours/notes)
    to generate a short 5-10 word motivational nudge for the user.

    Request payload:
    - library_hdr_guid: The book the user is reading.
    - reward_hdr_guid: Optional reward header for milestone evaluation context.
    """
    try:
        result = await AgentTriggerService.trigger_milestone_quote_agent(
            library_hdr_guid=request.library_hdr_guid,
            reward_hdr_guid=request.reward_hdr_guid,
        )

        quote = result.responses[0] if result.responses else None

        response = MilestoneQuoteResponse(
            session_id=result.session_id,
            quote=quote,
            responses=result.responses,
        )
        return ApiResponse.success(response)

    except ValueError as ve:
        return ApiResponse.error({"message": str(ve)})
    except Exception as e:
        logger.error(f"Milestone quote agent trigger error: {e}", exc_info=True)
        error_result = MilestoneQuoteResponse(
            session_id="error",
            responses=[str(e)],
        )
        return ApiResponse.error(error_result)