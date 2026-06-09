from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime
from util.supabase_config import supabase
from model.notebook.app_mm_notebook_content import AppMmNotebookContentCreate, AppMmNotebookContentUpdate, AppMmNotebookContentResponse

class AppMmNotebookContentService:
    TABLE_NAME = "app_mm_notebook_content"
    
    @staticmethod
    def create_notebook_content(content_data: AppMmNotebookContentCreate) -> AppMmNotebookContentResponse:
        """Create a new notebook content entry"""
        new_content = {
            "guid": str(uuid4()),
            "user_guid": str(content_data.user_guid),
            "notebook_hdr_guid": str(content_data.notebook_hdr_guid),
            "library_hdr_guid": str(content_data.library_hdr_guid) if content_data.library_hdr_guid else None,
            "focus_session_guid": str(content_data.focus_session_guid) if content_data.focus_session_guid else None,
            "content_text": content_data.content_text,
            "image_url": content_data.image_url,
            "highlight_metadata": content_data.highlight_metadata,
            "sequence_no": content_data.sequence_no,
            "updated_date": datetime.now().isoformat()
        }
        
        response = supabase.table(AppMmNotebookContentService.TABLE_NAME).insert(new_content).execute()
        
        if not response.data:
            raise Exception("Failed to create notebook content")
        
        return AppMmNotebookContentResponse(**response.data[0])
    
    @staticmethod
    def get_notebook_content_by_id(content_id: UUID) -> Optional[AppMmNotebookContentResponse]:
        """Get notebook content by GUID"""
        response = supabase.table(AppMmNotebookContentService.TABLE_NAME).select("*").eq("guid", str(content_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmNotebookContentResponse(**response.data[0])
    
    @staticmethod
    def get_all_notebook_contents() -> List[AppMmNotebookContentResponse]:
        """Get all notebook contents"""
        response = supabase.table(AppMmNotebookContentService.TABLE_NAME).select("*").execute()
        
        return [AppMmNotebookContentResponse(**content) for content in response.data]
    
    @staticmethod
    def get_contents_by_notebook_hdr(notebook_hdr_guid: UUID) -> List[AppMmNotebookContentResponse]:
        """Get all contents for a specific notebook header"""
        response = supabase.table(AppMmNotebookContentService.TABLE_NAME).select("*").eq("notebook_hdr_guid", str(notebook_hdr_guid)).order("sequence_no").execute()
        
        return [AppMmNotebookContentResponse(**content) for content in response.data]
    
    @staticmethod
    def get_contents_by_user(user_guid: UUID) -> List[AppMmNotebookContentResponse]:
        """Get all contents for a specific user"""
        response = supabase.table(AppMmNotebookContentService.TABLE_NAME).select("*").eq("user_guid", str(user_guid)).order("created_date", desc=True).execute()
        
        return [AppMmNotebookContentResponse(**content) for content in response.data]
    
    @staticmethod
    def update_notebook_content(content_id: UUID, content_data: AppMmNotebookContentUpdate) -> Optional[AppMmNotebookContentResponse]:
        """Update notebook content by GUID"""
        update_data = content_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return AppMmNotebookContentService.get_notebook_content_by_id(content_id)
        
        # Convert UUIDs to strings for Supabase
        if "user_guid" in update_data:
            update_data["user_guid"] = str(update_data["user_guid"])
        if "notebook_hdr_guid" in update_data:
            update_data["notebook_hdr_guid"] = str(update_data["notebook_hdr_guid"])
        if "library_hdr_guid" in update_data:
            update_data["library_hdr_guid"] = str(update_data["library_hdr_guid"]) if update_data["library_hdr_guid"] else None
        if "focus_session_guid" in update_data:
            update_data["focus_session_guid"] = str(update_data["focus_session_guid"]) if update_data["focus_session_guid"] else None
        
        update_data["updated_date"] = datetime.now().isoformat()
        
        response = supabase.table(AppMmNotebookContentService.TABLE_NAME).update(update_data).eq("guid", str(content_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmNotebookContentResponse(**response.data[0])
    
    @staticmethod
    def delete_notebook_content(content_id: UUID) -> bool:
        """Delete notebook content by GUID"""
        response = supabase.table(AppMmNotebookContentService.TABLE_NAME).delete().eq("guid", str(content_id)).execute()
        
        return len(response.data) > 0

    @staticmethod
    def get_notes_by_focus_session(focus_session_guid: UUID) -> str:
        """Get all note content for a focus session as a formatted string.

        Queries notebook content records by focus_session_guid ordered by
        created_date descending and returns them as a numbered list.

        Args:
            focus_session_guid: The UUID of the focus session.

        Returns:
            A string with notes formatted as:
            "note 1: ...\\nnote 2: ...\\nnote 3: ..."
            Returns empty string if no notes found.
        """
        response = (
            supabase.table(AppMmNotebookContentService.TABLE_NAME)
            .select("content_text, created_date")
            .eq("focus_session_guid", str(focus_session_guid))
            .order("created_date", desc=True)
            .execute()
        )

        if not response.data:
            return ""

        output_lines = []
        for i, record in enumerate(response.data, start=1):
            content = record.get("content_text") or ""
            if content.strip():
                output_lines.append(f"note {i}: {content.strip()}")

        return "\n".join(output_lines)