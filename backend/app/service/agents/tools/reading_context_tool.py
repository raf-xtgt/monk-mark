# backend/app/service/agents/tools/reading_context_tool.py
# Source: adk-local-docs/docs/tools-custom/function-tools.md

import re
import logging
from uuid import UUID
from typing import Optional

from service.library.app_mm_library_hdr_service import AppMmLibraryHdrService
from service.notebook.app_mm_notebook_content_service import AppMmNotebookContentService
from service.notebook.app_mm_notebook_llm_chat_transcript_service import NotebookLlmChatTranscriptService

logger = logging.getLogger(__name__)

MAX_CONTEXT_CHARS = 30000


def build_reading_context(
    user_guid: str,
    library_hdr_guid: str,
    notebook_hdr_guid: str,
    llm_chat_hdr_guid: Optional[str] = None,
    max_chars: int = MAX_CONTEXT_CHARS,
) -> dict:
    """Retrieves, flattens, cleans, and sanitizes user reading data into a prompt-ready string.

    Combines book metadata, notebook content (notes/highlights), and prior chat transcripts
    into a single sanitized text string for use as agent prompt context.

    Args:
        user_guid: The UUID of the user.
        library_hdr_guid: The UUID of the library header (book).
        notebook_hdr_guid: The UUID of the notebook header.
        llm_chat_hdr_guid: Optional UUID of the LLM chat header for transcript retrieval.
        max_chars: Maximum character limit for the output string. Defaults to 30000.

    Returns:
        dict with 'status' and either 'context'+'notebook_content_count' or error details.
    """
    try:
        sections = []
        notebook_content_count = 0

        # 1. Book metadata
        book = AppMmLibraryHdrService.get_library_hdr_by_id(UUID(library_hdr_guid))
        if book:
            sections.append(
                f"## Book: {book.book_name}\n{book.book_desc or 'No description available.'}"
            )

        # 2. Notebook content (notes and highlights)
        contents = AppMmNotebookContentService.get_contents_by_notebook_hdr(
            UUID(notebook_hdr_guid)
        )
        if contents:
            notebook_content_count = len(contents)
            notes_text = "\n".join(
                f"- [{c.sequence_no}] {c.content_text}"
                for c in contents
                if c.content_text
            )
            sections.append(
                f"## Notes and Highlights ({notebook_content_count} entries)\n{notes_text}"
            )

        # 3. Chat transcripts (if llm_chat_hdr_guid provided)
        if llm_chat_hdr_guid:
            transcripts = NotebookLlmChatTranscriptService.get_transcripts_by_chat_hdr(
                UUID(llm_chat_hdr_guid)
            )
            if transcripts:
                transcript_text = "\n".join(
                    f"[{t.sender}]: {t.msg_content}"
                    for t in transcripts
                    if t.msg_content
                )
                sections.append(
                    f"## Prior Conversations ({len(transcripts)} messages)\n{transcript_text}"
                )

        # 4. Flatten and clean
        raw_text = "\n\n".join(sections)
        # Strip HTML tags
        cleaned = re.sub(r"<[^>]+>", "", raw_text)
        # Remove non-printable characters (keep newlines, tabs)
        cleaned = re.sub(r"[^\x20-\x7E\n\t]", "", cleaned)
        # Collapse excessive whitespace
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

        # 5. Truncate
        if len(cleaned) > max_chars:
            cleaned = cleaned[:max_chars] + "\n\n[...truncated at character limit]"

        return {
            "status": "success",
            "context": cleaned,
            "notebook_content_count": notebook_content_count,
        }
    except Exception as e:
        logger.error(f"build_reading_context error: {e}", exc_info=True)
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e),
        }
