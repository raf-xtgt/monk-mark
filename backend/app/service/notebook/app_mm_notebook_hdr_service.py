from uuid import UUID, uuid4
from typing import List, Optional
from util.supabase_config import supabase
from model.notebook.app_mm_notebook_hdr import AppMmNotebookHdrCreate, AppMmNotebookHdrUpdate, AppMmNotebookHdrResponse

class AppMmNotebookHdrService:
    TABLE_NAME = "app_mm_notebook_hdr"
    
    @staticmethod
    def create_notebook_hdr(notebook_hdr_data: AppMmNotebookHdrCreate) -> AppMmNotebookHdrResponse:
        """Create a new notebook header"""
        new_notebook_hdr = {
            "guid": str(uuid4()),
            "user_guid": str(notebook_hdr_data.user_guid),
            "library_hdr_guid": str(notebook_hdr_data.library_hdr_guid),
            "running_no": notebook_hdr_data.running_no,
            "name": notebook_hdr_data.name
        }
        
        response = supabase.table(AppMmNotebookHdrService.TABLE_NAME).insert(new_notebook_hdr).execute()
        
        if not response.data:
            raise Exception("Failed to create notebook header")
        
        return AppMmNotebookHdrResponse(**response.data[0])
    
    @staticmethod
    def get_notebook_hdr_by_id(notebook_hdr_id: UUID) -> Optional[AppMmNotebookHdrResponse]:
        """Get notebook header by GUID"""
        response = supabase.table(AppMmNotebookHdrService.TABLE_NAME).select("*").eq("guid", str(notebook_hdr_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmNotebookHdrResponse(**response.data[0])
    
    @staticmethod
    def get_all_notebook_hdrs() -> List[AppMmNotebookHdrResponse]:
        """Get all notebook headers"""
        response = supabase.table(AppMmNotebookHdrService.TABLE_NAME).select("*").execute()
        
        return [AppMmNotebookHdrResponse(**notebook_hdr) for notebook_hdr in response.data]
    
    @staticmethod
    def get_notebook_hdrs_by_user(user_guid: UUID) -> List[AppMmNotebookHdrResponse]:
        """Get all notebook headers for a specific user"""
        response = supabase.table(AppMmNotebookHdrService.TABLE_NAME).select("*").eq("user_guid", str(user_guid)).execute()
        
        return [AppMmNotebookHdrResponse(**notebook_hdr) for notebook_hdr in response.data]
    
    @staticmethod
    def get_notebook_hdrs_by_library(library_hdr_guid: UUID) -> Optional[AppMmNotebookHdrResponse]:
        """Get first notebook header for a specific library"""
        response = supabase.table(AppMmNotebookHdrService.TABLE_NAME).select("*").eq("library_hdr_guid", str(library_hdr_guid)).limit(1).execute()
        
        if not response.data:
            return None
        
        return AppMmNotebookHdrResponse(**response.data[0])
    
    @staticmethod
    def update_notebook_hdr(notebook_hdr_id: UUID, notebook_hdr_data: AppMmNotebookHdrUpdate) -> Optional[AppMmNotebookHdrResponse]:
        """Update notebook header by GUID"""
        update_data = notebook_hdr_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return AppMmNotebookHdrService.get_notebook_hdr_by_id(notebook_hdr_id)
        
        response = supabase.table(AppMmNotebookHdrService.TABLE_NAME).update(update_data).eq("guid", str(notebook_hdr_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmNotebookHdrResponse(**response.data[0])
    
    @staticmethod
    def delete_notebook_hdr(notebook_hdr_id: UUID) -> bool:
        """Delete notebook header by GUID"""
        response = supabase.table(AppMmNotebookHdrService.TABLE_NAME).delete().eq("guid", str(notebook_hdr_id)).execute()
        
        return len(response.data) > 0
