# backend/app/service/agents/tools/agent_context_util.py

import logging
from uuid import UUID
from typing import Optional

from service.library.app_mm_library_hdr_service import AppMmLibraryHdrService
from service.notebook.app_mm_notebook_llm_chat_transcript_service import NotebookLlmChatTranscriptService
from service.notebook.app_mm_notebook_content_service import AppMmNotebookContentService

logger = logging.getLogger(__name__)


def build_socratic_agent_context(
    focus_session_guid: Optional[str] = None,
    library_hdr_guid: Optional[str] = None,
) -> str:
    """Build a compiled context string for the socratic dialogue agent.

    Combines the book title, last 3 conversation turns, and notes taken
    during the current focus session into a single prompt-ready string.

    Args:
        focus_session_guid: The UUID string of the current focus session.
        library_hdr_guid: The UUID string of the library header (book).

    Returns:
        A formatted context string. Returns empty string if no data is available.
    """
    sections = []

    # 1. Book title
    if library_hdr_guid:
        try:
            book_title = AppMmLibraryHdrService.get_book_title(UUID(library_hdr_guid))
            if book_title:
                sections.append(f"Book title: {book_title}")
        except Exception as e:
            logger.error(f"Error fetching book title: {e}")

    # 2. Last 3 conversation turns
    if focus_session_guid:
        try:
            conversation = NotebookLlmChatTranscriptService.get_chat_transcripts_by_focus_session(
                UUID(focus_session_guid)
            )
            if conversation:
                sections.append(f"Last conversation:\n{conversation}")
        except Exception as e:
            logger.error(f"Error fetching conversation turns: {e}")

    # 3. Notes taken during this session
    if focus_session_guid:
        try:
            notes = AppMmNotebookContentService.get_notes_by_focus_session(
                UUID(focus_session_guid)
            )
            if notes:
                sections.append(f"Notes taken:\n{notes}")
        except Exception as e:
            logger.error(f"Error fetching notes: {e}")

    return "\n\n".join(sections)

def build_gitlab_agent_context(
    focus_session_guid: Optional[str] = None,
    library_hdr_guid: Optional[str] = None,
) -> list:
    """Build a multi-part Content message for the GitLab agent.

    Combines book title, last 10 conversation turns, and notes with their
    highlighted reference images into an interleaved list of types.Part objects
    suitable for passing as a multimodal Gemini Content message.

    The resulting parts list looks like:
        [Part(text="Book title: ...\\n\\nLast conversation:\\nuser: ...\\n..."),
         Part(text="Notes taken:\\nnote-1: ...\\nreference image:"),
         Part(inline_data=<image-bytes>),
         Part(text="note-2: ...\\nreference image:"),
         Part(inline_data=<image-bytes>),
         ...]

    Args:
        focus_session_guid: The UUID string of the current focus session.
        library_hdr_guid: The UUID string of the library header (book).

    Returns:
        A list of google.genai types.Part objects for constructing a Content message.
    """
    from google.genai import types as genai_types
    from service.notebook.app_mm_notebook_content_file_link_service import NotebookContentFileLinkService
    import asyncio

    parts: list = []
    text_sections: list[str] = []

    # 1. Book title
    if library_hdr_guid:
        try:
            book_title = AppMmLibraryHdrService.get_book_title(UUID(library_hdr_guid))
            if book_title:
                text_sections.append(f"Book title: {book_title}")
        except Exception as e:
            logger.error(f"Error fetching book title: {e}")

    # 2. Last 10 conversation turns
    if focus_session_guid:
        try:
            conversation = NotebookLlmChatTranscriptService.get_chat_transcripts_by_focus_session(
                UUID(focus_session_guid), turns=10
            )
            if conversation:
                text_sections.append(f"Last conversation:\n{conversation}")
        except Exception as e:
            logger.error(f"Error fetching conversation turns: {e}")

    # Add the text preamble (book title + conversation) as the first part
    if text_sections:
        parts.append(genai_types.Part(text="\n\n".join(text_sections)))

    # 3. Notes with interleaved reference images
    if focus_session_guid:
        try:
            # build_image_and_note_context is async — run it in the current event loop
            # or create one if none is running
            try:
                loop = asyncio.get_running_loop()
                # We're already in an async context — use a helper
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    note_dtos = loop.run_in_executor(pool, lambda: None)
                # Fallback: since we can't easily await here, use asyncio.run in a thread
                # Instead, we'll call the sync parts directly
                raise RuntimeError("Use sync fallback")
            except RuntimeError:
                # No running loop or fallback — run synchronously
                note_dtos = asyncio.run(
                    NotebookContentFileLinkService.build_image_and_note_context(UUID(focus_session_guid))
                )

            if note_dtos:
                parts.append(genai_types.Part(text="Notes taken:"))

                seen_refs: set[str] = set()
                note_counter = 0

                for dto in note_dtos:
                    # Avoid duplicating the same note text for multiple images of the same content
                    is_new_note = dto.image_ref not in seen_refs
                    if is_new_note:
                        note_counter += 1
                        seen_refs.add(dto.image_ref)
                        parts.append(genai_types.Part(
                            text=f"note-{note_counter}: {dto.note_content}"
                        ))

                    # Attach the reference image if available
                    if dto.temp_image_file:
                        try:
                            with open(dto.temp_image_file, "rb") as img_f:
                                image_bytes = img_f.read()
                            parts.append(genai_types.Part(text="reference image:"))
                            parts.append(genai_types.Part.from_bytes(
                                data=image_bytes,
                                mime_type="image/png",
                            ))
                        except OSError as img_err:
                            logger.warning(f"Could not read temp image {dto.temp_image_file}: {img_err}")
                        finally:
                            # Clean up temp file
                            try:
                                import os as _os
                                _os.unlink(dto.temp_image_file)
                            except OSError:
                                pass

        except Exception as e:
            logger.error(f"Error building image and note context: {e}", exc_info=True)

    return parts


def build_art_evolution_agent_context(
    visual_motif: Optional[str] = None,
    library_hdr_guid: Optional[str] = None,
    user_guid: Optional[str] = None,
) -> dict:
    """Build context for the art evolution agent.

    Fetches the previous milestone image URL and tier level from the reward system,
    then downloads the image to a temporary file for multimodal injection.

    Args:
        visual_motif: A single-sentence abstract visual description for the evolution.
        library_hdr_guid: The UUID string of the library header (book).
        user_guid: The UUID string of the user.

    Returns:
        dict with:
            - status: "success" or "error"
            - visual_motif: The input visual motif string
            - previous_tier: The previous tier level (int)
            - previous_image_url: The URL of the previous artwork
            - temp_image_file: Path to the downloaded image on disk (temporary file)
        On error:
            - status: "error"
            - message: Error description
    """
    import io
    import tempfile
    import httpx

    from service.reward.app_mm_reward_hdr_service import AppMmRewardHdrService
    from service.reward.app_mm_reward_line_service import AppMmRewardLineService
    from util.supabase_config import supabase

    try:
        if not library_hdr_guid:
            return {
                "status": "error",
                "message": "No library_hdr_guid provided.",
            }

        # Find the reward_hdr for this library
        reward_hdr_response = (
            supabase.table(AppMmRewardHdrService.TABLE_NAME)
            .select("guid")
            .eq("llibrary_hdr_guid", str(library_hdr_guid))
            .order("tier_level", desc=True)
            .limit(1)
            .execute()
        )

        if not reward_hdr_response.data:
            return {
                "status": "error",
                "message": "No reward header found for this library.",
            }

        reward_hdr_guid = reward_hdr_response.data[0]["guid"]

        # Get the highest tier reward line
        latest_reward_line = AppMmRewardLineService.get_highest_tier_by_reward_hdr(reward_hdr_guid)

        if not latest_reward_line:
            return {
                "status": "error",
                "message": "No previous reward line found. This may be the first generation.",
            }

        previous_image_url = latest_reward_line.image_url
        previous_tier = latest_reward_line.tier_level or 0

        if not previous_image_url:
            return {
                "status": "error",
                "message": "No previous image URL found in reward lines.",
            }

        # Download the image to a temporary file
        logger.info(f"Downloading previous art image from: {previous_image_url}")
        response = httpx.get(previous_image_url, timeout=30.0, follow_redirects=True)
        response.raise_for_status()

        temp_file = tempfile.NamedTemporaryFile(
            suffix=".png", prefix="art_evolution_ref_", delete=False
        )
        temp_file.write(response.content)
        temp_file_path = temp_file.name
        temp_file.close()

        logger.info(f"Previous art image saved to: {temp_file_path}")

        return {
            "status": "success",
            "visual_motif": visual_motif,
            "previous_tier": previous_tier,
            "previous_image_url": previous_image_url,
            "temp_image_file": temp_file_path,
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to download previous art image: HTTP {e.response.status_code}", exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to download previous art image: HTTP {e.response.status_code}",
        }
    except Exception as e:
        logger.error(f"build_art_evolution_agent_context error: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to build art evolution context: {str(e)}",
        }


def build_milestone_quote_agent_context(
    reward_hdr_guid: Optional[str] = None,
    library_hdr_guid: Optional[str] = None,
) -> str:
    """Build a context string for the milestone quote/mantra agent.

    Combines the book title with milestone progression data (current tier,
    remaining hours and notes) into a prompt-ready string.

    Args:
        reward_hdr_guid: The UUID string of the reward header record.
        library_hdr_guid: The UUID string of the library header (book).

    Returns:
        A formatted context string. Returns empty string if no data is available.
    """
    from service.reward.app_mm_reward_hdr_service import AppMmRewardHdrService

    sections = []

    # 1. Book title
    if library_hdr_guid:
        try:
            book_title = AppMmLibraryHdrService.get_book_title(UUID(library_hdr_guid))
            if book_title:
                sections.append(f"Book title: {book_title}")
        except Exception as e:
            logger.error(f"Error fetching book title: {e}")

    # 2. Milestone evaluation from reward_hdr
    if reward_hdr_guid:
        try:
            reward_hdr = AppMmRewardHdrService.get_reward_hdr_by_id(UUID(reward_hdr_guid))
            if reward_hdr and reward_hdr.user_guid and reward_hdr.library_hdr_guid:
                # Get the full reward summary which includes milestone evaluation
                reward_summary = AppMmRewardHdrService.get_reward_summary_by_library(
                    user_guid=reward_hdr.user_guid,
                    library_hdr_guid=reward_hdr.library_hdr_guid,
                )
                evaluation = reward_summary.milestone_evaluation

                if evaluation:
                    progress_lines = [
                        "Reading progress:",
                        f"Current evolution: {evaluation.current_tier}",
                    ]

                    if evaluation.remaining_hours is not None and evaluation.remaining_notes is not None:
                        progress_lines.append(
                            f"User needs {evaluation.remaining_hours} hours and "
                            f"{evaluation.remaining_notes} notes to unlock the next evolution."
                        )
                    elif evaluation.remaining_hours is not None:
                        progress_lines.append(
                            f"User needs {evaluation.remaining_hours} more hours to unlock the next evolution."
                        )
                    elif evaluation.remaining_notes is not None:
                        progress_lines.append(
                            f"User needs {evaluation.remaining_notes} more notes to unlock the next evolution."
                        )
                    else:
                        progress_lines.append("User has fulfilled all requirements for the next evolution.")

                    sections.append("\n".join(progress_lines))
        except Exception as e:
            logger.error(f"Error fetching milestone evaluation: {e}", exc_info=True)

    return "\n\n".join(sections)