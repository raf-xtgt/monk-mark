# backend/app/service/agents/tools/save_conversation_turn_tool.py
# Source: adk-local-docs/docs/tools-custom/function-tools.md
# Tool that persists user and assistant messages to the chat transcript table.
# Uses ToolContext to read session state directly, avoiding LLM hallucination of GUIDs.

import logging
from uuid import UUID

from google.adk.tools import ToolContext

from service.notebook.app_mm_notebook_llm_chat_transcript_service import (
    NotebookLlmChatTranscriptService,
)
from model.notebook.app_mm_notebook_llm_chat_transcript import (
    AppMmNotebookLlmChatTranscriptCreate,
)

logger = logging.getLogger(__name__)


def save_conversation_turn(
    user_message: str,
    assistant_message: str,
    tool_context: ToolContext,
) -> dict:
    """Persists a conversation turn (user message + assistant response) to the database.

    This tool MUST be called after every substantive exchange to maintain
    a complete conversation history for future context retrieval.
    The user_guid and llm_chat_hdr_guid are read directly from session state
    to ensure correctness.

    Args:
        user_message: The user's transcribed spoken input or text message.
        assistant_message: The assistant's response text that was spoken back to the user.
        tool_context: ADK ToolContext (automatically injected) — provides access to session state.

    Returns:
        dict with 'status' and confirmation or error details.
    """
    try:
        # Read identifiers from session state (set during WebSocket handshake)
        user_guid = tool_context.state.get("user_guid")
        llm_chat_hdr_guid = tool_context.state.get("llm_chat_hdr_guid")
        focus_session_guid = tool_context.state.get("focus_session_guid")

        if not user_guid or not llm_chat_hdr_guid:
            logger.warning(
                "save_conversation_turn skipped: missing session state "
                f"(user_guid={user_guid}, llm_chat_hdr_guid={llm_chat_hdr_guid})"
            )
            return {
                "status": "skipped",
                "message": "user_guid or llm_chat_hdr_guid not found in session state.",
            }

        saved_count = 0

        # Save user message
        if user_message and user_message.strip():
            user_transcript = AppMmNotebookLlmChatTranscriptCreate(
                user_guid=UUID(user_guid),
                llm_chat_hdr_guid=UUID(llm_chat_hdr_guid),
                msg_content=user_message.strip(),
                sender="user",
                focus_session_guid=UUID(focus_session_guid) if focus_session_guid else None,
            )
            NotebookLlmChatTranscriptService.create_transcript(user_transcript)
            saved_count += 1
            logger.info(
                f"Saved user message for chat {llm_chat_hdr_guid}: "
                f"{user_message[:80]}..."
            )

        # Save assistant message
        if assistant_message and assistant_message.strip():
            assistant_transcript = AppMmNotebookLlmChatTranscriptCreate(
                user_guid=UUID(user_guid),
                llm_chat_hdr_guid=UUID(llm_chat_hdr_guid),
                msg_content=assistant_message.strip(),
                sender="assistant",
                focus_session_guid=UUID(focus_session_guid) if focus_session_guid else None,
            )
            NotebookLlmChatTranscriptService.create_transcript(assistant_transcript)
            saved_count += 1
            logger.info(
                f"Saved assistant message for chat {llm_chat_hdr_guid}: "
                f"{assistant_message[:80]}..."
            )

        return {
            "status": "success",
            "messages_saved": saved_count,
        }

    except Exception as e:
        logger.error(f"save_conversation_turn error: {e}", exc_info=True)
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e),
        }
