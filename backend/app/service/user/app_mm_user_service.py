from uuid import UUID, uuid4
from typing import List, Optional
from util.supabase_config import supabase
from model.user.app_mm_user import AppMmUserCreate, AppMmUserUpdate, AppMmUserResponse

class AppMmUserService:
    TABLE_NAME = "app_mm_user"
    
    @staticmethod
    def create_user(user_data: AppMmUserCreate) -> AppMmUserResponse:
        """Create a new user"""
        new_user = {
            "guid": str(uuid4()),
            "email": user_data.email
        }
        
        response = supabase.table(AppMmUserService.TABLE_NAME).insert(new_user).execute()
        
        if not response.data:
            raise Exception("Failed to create user")
        
        return AppMmUserResponse(**response.data[0])
    
    @staticmethod
    def get_user_by_id(user_id: UUID) -> Optional[AppMmUserResponse]:
        """Get user by GUID"""
        response = supabase.table(AppMmUserService.TABLE_NAME).select("*").eq("guid", str(user_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmUserResponse(**response.data[0])
    
    @staticmethod
    def get_all_users() -> List[AppMmUserResponse]:
        """Get all users"""
        response = supabase.table(AppMmUserService.TABLE_NAME).select("*").execute()
        
        return [AppMmUserResponse(**user) for user in response.data]
    
    @staticmethod
    def update_user(user_id: UUID, user_data: AppMmUserUpdate) -> Optional[AppMmUserResponse]:
        """Update user by GUID"""
        update_data = user_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return AppMmUserService.get_user_by_id(user_id)
        
        response = supabase.table(AppMmUserService.TABLE_NAME).update(update_data).eq("guid", str(user_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmUserResponse(**response.data[0])
    
    @staticmethod
    def delete_user(user_id: UUID) -> bool:
        """Delete user by GUID"""
        response = supabase.table(AppMmUserService.TABLE_NAME).delete().eq("guid", str(user_id)).execute()
        
        return len(response.data) > 0
