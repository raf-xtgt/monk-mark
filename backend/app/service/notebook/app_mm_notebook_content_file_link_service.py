from uuid import UUID, uuid4
from typing import List, Optional
from util.supabase_config import supabase
from model.notebook.app_mm_notebook_content_file_link import (
    AppMmNotebookContentFileLinkCreate,
    AppMmNotebookContentFileLinkUpdate,
    AppMmNotebookContentFileLinkResponse
)

class NotebookContentFileLinkService:
    TABLE_NAME = "app_mm_notebook_content_file_link"
    
    @staticmethod
    def create(link_data: AppMmNotebookContentFileLinkCreate) -> AppMmNotebookContentFileLinkResponse:
        """Create a new notebook content file link"""
        new_link = {
            "guid": str(uuid4()),
            "user_guid": str(link_data.user_guid),
            "notebook_hdr_guid": str(link_data.notebook_hdr_guid),
            "notebook_content_guid": str(link_data.notebook_content_guid) if link_data.notebook_content_guid else None,
            "file_upload_guid": str(link_data.file_upload_guid) if link_data.file_upload_guid else None,
            "image_url": link_data.image_url,
            "highlight_metadata": link_data.highlight_metadata
        }
        
        response = supabase.table(NotebookContentFileLinkService.TABLE_NAME).insert(new_link).execute()
        
        if not response.data:
            raise Exception("Failed to create notebook content file link")
        
        return AppMmNotebookContentFileLinkResponse(**response.data[0])
    
    @staticmethod
    def get_by_guid(link_id: UUID) -> Optional[AppMmNotebookContentFileLinkResponse]:
        """Get notebook content file link by GUID"""
        response = supabase.table(NotebookContentFileLinkService.TABLE_NAME).select("*").eq("guid", str(link_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmNotebookContentFileLinkResponse(**response.data[0])
    
    @staticmethod
    def get_all() -> List[AppMmNotebookContentFileLinkResponse]:
        """Get all notebook content file links"""
        response = supabase.table(NotebookContentFileLinkService.TABLE_NAME).select("*").execute()
        
        return [AppMmNotebookContentFileLinkResponse(**link) for link in response.data]
    
    @staticmethod
    def get_by_user(user_guid: UUID) -> List[AppMmNotebookContentFileLinkResponse]:
        """Get all notebook content file links by user GUID"""
        response = supabase.table(NotebookContentFileLinkService.TABLE_NAME).select("*").eq("user_guid", str(user_guid)).execute()
        
        return [AppMmNotebookContentFileLinkResponse(**link) for link in response.data]
    
    @staticmethod
    def get_by_notebook_hdr(notebook_hdr_guid: UUID) -> List[AppMmNotebookContentFileLinkResponse]:
        """Get all notebook content file links by notebook header GUID"""
        response = supabase.table(NotebookContentFileLinkService.TABLE_NAME).select("*").eq("notebook_hdr_guid", str(notebook_hdr_guid)).execute()
        
        return [AppMmNotebookContentFileLinkResponse(**link) for link in response.data]
    
    @staticmethod
    def get_by_notebook_content(notebook_content_guid: UUID) -> List[AppMmNotebookContentFileLinkResponse]:
        """Get all notebook content file links by notebook content GUID"""
        response = supabase.table(NotebookContentFileLinkService.TABLE_NAME).select("*").eq("notebook_content_guid", str(notebook_content_guid)).execute()
        
        return [AppMmNotebookContentFileLinkResponse(**link) for link in response.data]
    
    @staticmethod
    def get_by_file_upload(file_upload_guid: UUID) -> List[AppMmNotebookContentFileLinkResponse]:
        """Get all notebook content file links by file upload GUID"""
        response = supabase.table(NotebookContentFileLinkService.TABLE_NAME).select("*").eq("file_upload_guid", str(file_upload_guid)).execute()
        
        return [AppMmNotebookContentFileLinkResponse(**link) for link in response.data]
    
    @staticmethod
    def update(link_id: UUID, link_data: AppMmNotebookContentFileLinkUpdate) -> Optional[AppMmNotebookContentFileLinkResponse]:
        """Update notebook content file link by GUID"""
        update_data = link_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return NotebookContentFileLinkService.get_by_guid(link_id)
        
        # Convert UUID fields to strings
        if "user_guid" in update_data:
            update_data["user_guid"] = str(update_data["user_guid"])
        if "notebook_hdr_guid" in update_data:
            update_data["notebook_hdr_guid"] = str(update_data["notebook_hdr_guid"])
        if "notebook_content_guid" in update_data:
            update_data["notebook_content_guid"] = str(update_data["notebook_content_guid"]) if update_data["notebook_content_guid"] else None
        if "file_upload_guid" in update_data:
            update_data["file_upload_guid"] = str(update_data["file_upload_guid"]) if update_data["file_upload_guid"] else None
        
        response = supabase.table(NotebookContentFileLinkService.TABLE_NAME).update(update_data).eq("guid", str(link_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmNotebookContentFileLinkResponse(**response.data[0])
    
    @staticmethod
    def delete_by_guid(link_id: UUID) -> bool:
        """Delete notebook content file link by GUID"""
        response = supabase.table(NotebookContentFileLinkService.TABLE_NAME).delete().eq("guid", str(link_id)).execute()
        
        return len(response.data) > 0

    @staticmethod
    async def trigger_and_store_note(
        notebook_hdr_guid: UUID,
        notebook_content_guid: UUID,
        image_url: str,
        highlight_metadata: dict,
    ) -> dict:
        """Triggers the note-taking agent and stores the generated note.

        Calls AgentTriggerService.trigger_note_taking_agent with the highlighted
        image, then updates the corresponding notebook content record with the
        generated note text.

        Args:
            notebook_hdr_guid: The notebook header context.
            notebook_content_guid: The notebook content entry to update.
            image_url: Public URL of the source image.
            highlight_metadata: Dict with "highlights" key containing coordinate objects.

        Returns:
            dict with 'status', 'generated_note', and 'notebook_content' (updated record).
        """
        from service.agent_trigger.agent_trigger_service import AgentTriggerService
        from service.notebook.app_mm_notebook_content_service import AppMmNotebookContentService
        from model.notebook.app_mm_notebook_content import AppMmNotebookContentUpdate

        # 1. Trigger the note-taking agent
        result = await AgentTriggerService.trigger_note_taking_agent(
            notebook_hdr_guid=notebook_hdr_guid,
            notebook_content_guid=notebook_content_guid,
            image_url=image_url,
            highlight_metadata=highlight_metadata,
        )

        # 2. Extract the generated note from the agent response
        generated_note = result.responses[0] if result.responses else None

        if not generated_note:
            return {
                "status": "error",
                "message": "Note-taking agent did not produce a response.",
                "session_id": result.session_id,
            }

        # 3. Update the notebook content record with the generated note
        update_data = AppMmNotebookContentUpdate(content_text=generated_note)
        updated_content = AppMmNotebookContentService.update_notebook_content(
            notebook_content_guid, update_data
        )

        if not updated_content:
            return {
                "status": "error",
                "message": f"Failed to update notebook content {notebook_content_guid}.",
                "generated_note": generated_note,
                "session_id": result.session_id,
            }

        return {
            "status": "success",
            "generated_note": generated_note,
            "session_id": result.session_id,
            "notebook_content": updated_content.model_dump(mode="json"),
        }

    @staticmethod
    async def build_image_and_note_context(
        focus_session_guid: UUID,
    ) -> list:
        """Builds a list of GitlabNoteDto for all notes in a focus session.

        For each notebook content record in the session:
        1. Retrieves the content text (the note).
        2. Fetches corresponding file link records (images with highlights).
        3. Renders highlight overlays onto each image using render_highlight_overlay.
        4. Returns a list of GitlabNoteDto with the note content, temp image path,
           and an image_ref linking the rendered image to its parent note.

        Args:
            focus_session_guid: The UUID of the focus session.

        Returns:
            A list of GitlabNoteDto objects.
        """
        from service.notebook.app_mm_notebook_content_service import AppMmNotebookContentService
        from service.agents.tools.note_taking_tool import render_highlight_overlay
        from model.dto.gitlab_agent_context_dto import GitlabNoteDto

        result: list = []

        # 1. Get all notebook content for this focus session
        response = supabase.table("app_mm_notebook_content").select(
            "guid, content_text"
        ).eq(
            "focus_session_guid", str(focus_session_guid)
        ).order("sequence_no").execute()

        if not response.data:
            return result

        for content_record in response.data:
            content_guid = content_record["guid"]
            note_content = content_record.get("content_text") or ""

            # 2. Get file links for this content
            file_links = NotebookContentFileLinkService.get_by_notebook_content(UUID(content_guid))

            if not file_links:
                # Note has no attached images — include it with no image
                if note_content.strip():
                    result.append(GitlabNoteDto(
                        temp_image_file=None,
                        note_content=note_content,
                        image_ref=content_guid,
                    ))
                continue

            # 3. For each file link, render the highlight overlay
            for file_link in file_links:
                image_url = file_link.image_url
                highlight_metadata = file_link.highlight_metadata

                if not image_url:
                    continue

                temp_image_path = None
                if highlight_metadata and highlight_metadata.get("highlights"):
                    render_result = render_highlight_overlay(
                        image_url=image_url,
                        highlight_metadata=highlight_metadata,
                    )
                    if render_result.get("status") == "success":
                        temp_image_path = render_result.get("temp_file_path")

                result.append(GitlabNoteDto(
                    temp_image_file=temp_image_path,
                    note_content=note_content,
                    image_ref=content_guid,
                ))

        return result