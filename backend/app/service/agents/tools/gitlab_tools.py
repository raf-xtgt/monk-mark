"""
GitLab custom Python tools for branch and file operations.

Uses the python-gitlab library for fine-grained control over
repository operations (branch creation, file commits, updates).
"""

import os
import logging
from typing import Optional

import gitlab as python_gitlab

logger = logging.getLogger(__name__)

GITLAB_TOKEN = os.environ.get("GITLAB_PERSONAL_ACCESS_TOKEN", "")


def create_branch(project_id: str, branch_name: str, ref_branch: str = "main") -> str:
    """Creates a new branch in the GitLab project.

    Args:
        project_id: The GitLab project ID or path (e.g. "12345" or "group/project").
        branch_name: Name of the new branch to create.
        ref_branch: The source branch to create from. Defaults to "main".

    Returns:
        A success or error message string.
    """
    gl = python_gitlab.Gitlab("https://gitlab.com", private_token=GITLAB_TOKEN)
    project = gl.projects.get(project_id)
    try:
        project.branches.create({"branch": branch_name, "ref": ref_branch})
        return f"Success: Branch '{branch_name}' created from '{ref_branch}'."
    except Exception as e:
        return f"Error creating branch: {str(e)}"


def create_file(
    project_id: str,
    file_path: str,
    content: str,
    commit_message: str,
    branch_name: str,
) -> str:
    """Creates a new file in the specified branch and commits it.

    Args:
        project_id: The GitLab project ID or path.
        file_path: Path of the file to create (e.g. "docs/notes.md").
        content: The text content of the file.
        commit_message: A descriptive commit message.
        branch_name: The branch to commit to.

    Returns:
        A success or error message string.
    """
    gl = python_gitlab.Gitlab("https://gitlab.com", private_token=GITLAB_TOKEN)
    project = gl.projects.get(project_id)
    try:
        project.files.create({
            "file_path": file_path,
            "branch": branch_name,
            "content": content,
            "author_email": "agent@monkmark.local",
            "author_name": "MonkMark Agent",
            "commit_message": commit_message,
        })
        return f"Success: File '{file_path}' committed to branch '{branch_name}'."
    except Exception as e:
        return f"Error creating file: {str(e)}"


def update_file(
    project_id: str,
    file_path: str,
    content: str,
    commit_message: str,
    branch_name: str,
) -> str:
    """Updates an existing file in the specified branch and commits it.

    Args:
        project_id: The GitLab project ID or path.
        file_path: Path of the file to update.
        content: The new text content of the file.
        commit_message: A descriptive commit message.
        branch_name: The branch to commit to.

    Returns:
        A success or error message string.
    """
    gl = python_gitlab.Gitlab("https://gitlab.com", private_token=GITLAB_TOKEN)
    project = gl.projects.get(project_id)
    try:
        f = project.files.get(file_path=file_path, ref=branch_name)
        f.content = content
        f.save(branch=branch_name, commit_message=commit_message)
        return f"Success: File '{file_path}' updated on branch '{branch_name}'."
    except Exception as e:
        return f"Error updating file: {str(e)}"


# --- GitLab Context Builder ---

MAX_CONTEXT_CHARS = 30000


def build_gitlab_context(
    user_guid: str,
    library_hdr_guid: Optional[str] = None,
    notebook_hdr_guid: Optional[str] = None,
    llm_chat_hdr_guid: Optional[str] = None,
    max_chars: int = MAX_CONTEXT_CHARS,
) -> dict:
    """Builds a structured GitlabAgentContextDto from the user's reading data.

    Retrieves book metadata, notebook content (text + file links), and chat transcripts
    to provide full context for the GitLab agent.

    Args:
        user_guid: The UUID of the user.
        library_hdr_guid: Optional UUID of the library header (book).
        notebook_hdr_guid: Optional UUID of the notebook header.
        llm_chat_hdr_guid: Optional UUID of the LLM chat header for transcript retrieval.
        max_chars: Maximum character limit (reserved for future use).

    Returns:
        dict with 'status' and 'context' (serialized GitlabAgentContextDto) or error details.
    """
    from uuid import UUID
    from model.dto.gitlab_agent_context_dto import (
        GitlabAgentContextDto,
        NotebookFileContentDto,
        NotebookChatTranscriptDto,
    )
    from service.library.app_mm_library_hdr_service import AppMmLibraryHdrService
    from service.notebook.app_mm_notebook_hdr_service import AppMmNotebookHdrService
    from service.notebook.app_mm_notebook_content_service import AppMmNotebookContentService
    from service.notebook.app_mm_notebook_content_file_link_service import NotebookContentFileLinkService
    from service.notebook.app_mm_notebook_llm_chat_hdr_service import NotebookLlmChatHdrService
    from service.notebook.app_mm_notebook_llm_chat_transcript_service import NotebookLlmChatTranscriptService

    try:
        book_name: Optional[str] = None
        book_desc: Optional[str] = None
        notebook_name: Optional[str] = None
        notebook_content_text: list[str] = []
        notebook_content_file: list[NotebookFileContentDto] = []
        llm_chat_transcript: list[NotebookChatTranscriptDto] = []

        # 1. Library header (book metadata)
        if library_hdr_guid:
            book = AppMmLibraryHdrService.get_library_hdr_by_id(UUID(library_hdr_guid))
            if book:
                book_name = book.book_name
                book_desc = book.book_desc

        # 2. Notebook header
        if notebook_hdr_guid:
            notebook_hdr = AppMmNotebookHdrService.get_notebook_hdr_by_id(UUID(notebook_hdr_guid))
            if notebook_hdr:
                notebook_name = notebook_hdr.name

            # 3. Notebook content (text entries)
            contents = AppMmNotebookContentService.get_contents_by_notebook_hdr(UUID(notebook_hdr_guid))
            if contents:
                notebook_content_text = [
                    c.content_text for c in contents if c.content_text
                ]

            # 4. Notebook content file links
            file_links = NotebookContentFileLinkService.get_by_notebook_hdr(UUID(notebook_hdr_guid))
            if file_links:
                notebook_content_file = [
                    NotebookFileContentDto(
                        notebook_content_file_guid=fl.guid,
                        image_url=fl.image_url,
                    )
                    for fl in file_links
                    if fl.image_url
                ]

        # 5. LLM chat header validation + transcripts
        if llm_chat_hdr_guid:
            chat_hdr = NotebookLlmChatHdrService.get_chat_hdr_by_id(UUID(llm_chat_hdr_guid))
            if chat_hdr:
                transcripts = NotebookLlmChatTranscriptService.get_transcripts_by_chat_hdr(
                    UUID(llm_chat_hdr_guid)
                )
                if transcripts:
                    llm_chat_transcript = [
                        NotebookChatTranscriptDto(
                            chat_transcript_guid=t.guid,
                            sender=t.sender,
                            msg_content=t.msg_content,
                        )
                        for t in transcripts
                        if t.msg_content
                    ]

        # 6. Build the DTO
        context_dto = GitlabAgentContextDto(
            user_guid=UUID(user_guid),
            library_hdr_guid=UUID(library_hdr_guid) if library_hdr_guid else None,
            book_name=book_name,
            book_desc=book_desc,
            notebook_hdr_guid=UUID(notebook_hdr_guid) if notebook_hdr_guid else None,
            notebook_name=notebook_name,
            notebook_content_text=notebook_content_text,
            notebook_content_file=notebook_content_file,
            llm_chat_hdr_guid=UUID(llm_chat_hdr_guid) if llm_chat_hdr_guid else None,
            llm_chat_transcript=llm_chat_transcript,
        )

        return {
            "status": "success",
            "context": context_dto.model_dump(mode="json"),
        }
    except Exception as e:
        logger.error(f"build_gitlab_context error: {e}", exc_info=True)
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e),
        }
