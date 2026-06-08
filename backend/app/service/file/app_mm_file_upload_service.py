from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime
from util.supabase_config import supabase
from model.file.app_mm_file_upload import AppMmFileUploadCreate, AppMmFileUploadUpdate, AppMmFileUploadResponse

class AppMmFileUploadService:
    TABLE_NAME = "app_mm_file_upload"
    
    @staticmethod
    def create_file_upload(file_data: AppMmFileUploadCreate) -> AppMmFileUploadResponse:
        """Create a new file upload record"""
        new_file = {
            "guid": str(uuid4()),
            "user_guid": str(file_data.user_guid),
            "file_name": file_data.file_name,
            "mime_type": file_data.mime_type,
            "metadata": file_data.metadata,
            "storage_path": file_data.storage_path,
            "bucket_name": file_data.bucket_name,
            "is_public": file_data.is_public,
            "updated_date": datetime.now().isoformat()
        }
        
        response = supabase.table(AppMmFileUploadService.TABLE_NAME).insert(new_file).execute()
        
        if not response.data:
            raise Exception("Failed to create file upload record")
        
        return AppMmFileUploadResponse(**response.data[0])
    
    @staticmethod
    def get_file_upload_by_id(file_id: UUID) -> Optional[AppMmFileUploadResponse]:
        """Get file upload by GUID"""
        response = supabase.table(AppMmFileUploadService.TABLE_NAME).select("*").eq("guid", str(file_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmFileUploadResponse(**response.data[0])
    
    @staticmethod
    def get_all_file_uploads() -> List[AppMmFileUploadResponse]:
        """Get all file uploads"""
        response = supabase.table(AppMmFileUploadService.TABLE_NAME).select("*").execute()
        
        return [AppMmFileUploadResponse(**file) for file in response.data]
    
    @staticmethod
    def get_files_by_user(user_guid: UUID) -> List[AppMmFileUploadResponse]:
        """Get all files for a specific user"""
        response = supabase.table(AppMmFileUploadService.TABLE_NAME).select("*").eq("user_guid", str(user_guid)).order("created_date", desc=True).execute()
        
        return [AppMmFileUploadResponse(**file) for file in response.data]
    
    @staticmethod
    def get_files_by_mime_type(mime_type: str) -> List[AppMmFileUploadResponse]:
        """Get all files by mime type"""
        response = supabase.table(AppMmFileUploadService.TABLE_NAME).select("*").eq("mime_type", mime_type).order("created_date", desc=True).execute()
        
        return [AppMmFileUploadResponse(**file) for file in response.data]
    
    @staticmethod
    def update_file_upload(file_id: UUID, file_data: AppMmFileUploadUpdate) -> Optional[AppMmFileUploadResponse]:
        """Update file upload by GUID"""
        update_data = file_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return AppMmFileUploadService.get_file_upload_by_id(file_id)
        
        # Convert UUID to string for Supabase
        if "user_guid" in update_data:
            update_data["user_guid"] = str(update_data["user_guid"])
        
        update_data["updated_date"] = datetime.now().isoformat()
        
        response = supabase.table(AppMmFileUploadService.TABLE_NAME).update(update_data).eq("guid", str(file_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmFileUploadResponse(**response.data[0])
    
    @staticmethod
    def delete_file_upload(file_id: UUID) -> bool:
        """Delete file upload by GUID"""
        response = supabase.table(AppMmFileUploadService.TABLE_NAME).delete().eq("guid", str(file_id)).execute()
        
        return len(response.data) > 0
