from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime
from util.supabase_config import supabase
from model.notebook.app_mm_notebook_llm_chat_hdr import (
    AppMmNotebookLlmChatHdrCreate,
    AppMmNotebookLlmChatHdrUpdate,
    AppMmNotebookLlmChatHdrResponse
)

class NotebookLlmChatHdrService:
    TABLE_NAME = "app_mm_notebook_llm_chat_hdr"
    
    @staticmethod
    def create_chat_hdr(chat_hdr_data: AppMmNotebookLlmChatHdrCreate) -> AppMmNotebookLlmChatHdrResponse:
        """Create a new notebook LLM chat header"""
        new_chat_hdr = {
            "guid": str(uuid4()),
            "user_guid": str(chat_hdr_data.user_guid),
            "notebook_hdr_guid": str(chat_hdr_data.notebook_hdr_guid) if chat_hdr_data.notebook_hdr_guid else None,
            "library_hdr_guid": str(chat_hdr_data.library_hdr_guid) if chat_hdr_data.library_hdr_guid else None
        }
        
        response = supabase.table(NotebookLlmChatHdrService.TABLE_NAME).insert(new_chat_hdr).execute()
        
        if not response.data:
            raise Exception("Failed to create notebook LLM chat header")
        
        return AppMmNotebookLlmChatHdrResponse(**response.data[0])
    
    @staticmethod
    def get_chat_hdr_by_id(chat_hdr_id: UUID) -> Optional[AppMmNotebookLlmChatHdrResponse]:
        """Get notebook LLM chat header by GUID"""
        response = supabase.table(NotebookLlmChatHdrService.TABLE_NAME).select("*").eq("guid", str(chat_hdr_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmNotebookLlmChatHdrResponse(**response.data[0])
    
    @staticmethod
    def get_all_chat_hdrs() -> List[AppMmNotebookLlmChatHdrResponse]:
        """Get all notebook LLM chat headers"""
        response = supabase.table(NotebookLlmChatHdrService.TABLE_NAME).select("*").execute()
        
        return [AppMmNotebookLlmChatHdrResponse(**chat_hdr) for chat_hdr in response.data]
    
    @staticmethod
    def get_chat_hdrs_by_user(user_guid: UUID) -> List[AppMmNotebookLlmChatHdrResponse]:
        """Get all notebook LLM chat headers for a specific user"""
        response = supabase.table(NotebookLlmChatHdrService.TABLE_NAME).select("*").eq("user_guid", str(user_guid)).execute()
        
        return [AppMmNotebookLlmChatHdrResponse(**chat_hdr) for chat_hdr in response.data]
    
    @staticmethod
    def get_chat_hdrs_by_notebook(notebook_hdr_guid: UUID) -> List[AppMmNotebookLlmChatHdrResponse]:
        """Get all notebook LLM chat headers for a specific notebook"""
        response = supabase.table(NotebookLlmChatHdrService.TABLE_NAME).select("*").eq("notebook_hdr_guid", str(notebook_hdr_guid)).execute()
        
        return [AppMmNotebookLlmChatHdrResponse(**chat_hdr) for chat_hdr in response.data]
    
    @staticmethod
    def get_chat_hdrs_by_library(library_hdr_guid: UUID) -> List[AppMmNotebookLlmChatHdrResponse]:
        """Get all notebook LLM chat headers for a specific library"""
        response = supabase.table(NotebookLlmChatHdrService.TABLE_NAME).select("*").eq("library_hdr_guid", str(library_hdr_guid)).execute()
        
        return [AppMmNotebookLlmChatHdrResponse(**chat_hdr) for chat_hdr in response.data]
    
    @staticmethod
    def update_chat_hdr(chat_hdr_id: UUID, chat_hdr_data: AppMmNotebookLlmChatHdrUpdate) -> Optional[AppMmNotebookLlmChatHdrResponse]:
        """Update notebook LLM chat header by GUID"""
        update_data = chat_hdr_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return NotebookLlmChatHdrService.get_chat_hdr_by_id(chat_hdr_id)
        
        # Convert UUIDs to strings
        if "user_guid" in update_data:
            update_data["user_guid"] = str(update_data["user_guid"])
        if "notebook_hdr_guid" in update_data:
            update_data["notebook_hdr_guid"] = str(update_data["notebook_hdr_guid"]) if update_data["notebook_hdr_guid"] else None
        if "library_hdr_guid" in update_data:
            update_data["library_hdr_guid"] = str(update_data["library_hdr_guid"]) if update_data["library_hdr_guid"] else None
        
        # Add updated_date
        update_data["updated_date"] = datetime.now().isoformat()
        
        response = supabase.table(NotebookLlmChatHdrService.TABLE_NAME).update(update_data).eq("guid", str(chat_hdr_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmNotebookLlmChatHdrResponse(**response.data[0])
    
    @staticmethod
    def delete_chat_hdr(chat_hdr_id: UUID) -> bool:
        """Delete notebook LLM chat header by GUID"""
        response = supabase.table(NotebookLlmChatHdrService.TABLE_NAME).delete().eq("guid", str(chat_hdr_id)).execute()
        
        return len(response.data) > 0
