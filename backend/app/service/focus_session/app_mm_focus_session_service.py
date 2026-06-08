from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime
from util.supabase_config import supabase
from model.focus_session.app_mm_focus_session import (
    AppMmFocusSessionCreate,
    AppMmFocusSessionUpdate,
    AppMmFocusSessionResponse
)
from model.dto.focus_session_query_criteria import FocusSessionQueryCriteria

class AppMmFocusSessionService:
    TABLE_NAME = "app_mm_focus_session"
    
    @staticmethod
    def create_focus_session(focus_session_data: AppMmFocusSessionCreate) -> AppMmFocusSessionResponse:
        """Create a new focus session"""
        new_focus_session = {
            "guid": str(uuid4()),
            "user_guid": str(focus_session_data.user_guid),
            "library_hdr_guid": str(focus_session_data.library_hdr_guid),
            "time_hrs": float(focus_session_data.time_hrs) if focus_session_data.time_hrs else None,
            "time_seconds": focus_session_data.time_seconds,
            "updated_date": datetime.utcnow().isoformat()
        }
        
        response = supabase.table(AppMmFocusSessionService.TABLE_NAME).insert(new_focus_session).execute()
        
        if not response.data:
            raise Exception("Failed to create focus session")
        
        return AppMmFocusSessionResponse(**response.data[0])
    
    @staticmethod
    def get_focus_session_by_id(focus_session_id: UUID) -> Optional[AppMmFocusSessionResponse]:
        """Get focus session by GUID"""
        response = supabase.table(AppMmFocusSessionService.TABLE_NAME).select("*").eq("guid", str(focus_session_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmFocusSessionResponse(**response.data[0])
    
    @staticmethod
    def get_all_focus_sessions() -> List[AppMmFocusSessionResponse]:
        """Get all focus sessions"""
        response = supabase.table(AppMmFocusSessionService.TABLE_NAME).select("*").execute()
        
        return [AppMmFocusSessionResponse(**session) for session in response.data]
    
    @staticmethod
    def get_focus_sessions_by_user(user_guid: UUID) -> List[AppMmFocusSessionResponse]:
        """Get all focus sessions for a specific user"""
        response = supabase.table(AppMmFocusSessionService.TABLE_NAME).select("*").eq("user_guid", str(user_guid)).execute()
        
        return [AppMmFocusSessionResponse(**session) for session in response.data]
    
    @staticmethod
    def get_focus_sessions_by_library(library_hdr_guid: UUID) -> List[AppMmFocusSessionResponse]:
        """Get all focus sessions for a specific library header"""
        response = supabase.table(AppMmFocusSessionService.TABLE_NAME).select("*").eq("library_hdr_guid", str(library_hdr_guid)).execute()
        
        return [AppMmFocusSessionResponse(**session) for session in response.data]
    
    @staticmethod
    def get_focus_sessions_by_criteria(criteria: FocusSessionQueryCriteria) -> List[AppMmFocusSessionResponse]:
        """Get focus sessions by query criteria"""
        query = supabase.table(AppMmFocusSessionService.TABLE_NAME).select("*")
        
        # Apply filters based on provided criteria
        if criteria.guid:
            query = query.eq("guid", str(criteria.guid))
        if criteria.user_guid:
            query = query.eq("user_guid", str(criteria.user_guid))
        if criteria.library_hdr_guid:
            query = query.eq("library_hdr_guid", str(criteria.library_hdr_guid))
        
        response = query.execute()
        
        return [AppMmFocusSessionResponse(**session) for session in response.data]
    
    @staticmethod
    def update_focus_session(focus_session_id: UUID, focus_session_data: AppMmFocusSessionUpdate) -> Optional[AppMmFocusSessionResponse]:
        """Update focus session by GUID"""
        update_data = focus_session_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return AppMmFocusSessionService.get_focus_session_by_id(focus_session_id)
        
        # Convert UUID fields to strings
        if "user_guid" in update_data:
            update_data["user_guid"] = str(update_data["user_guid"])
        if "library_hdr_guid" in update_data:
            update_data["library_hdr_guid"] = str(update_data["library_hdr_guid"])
        if "time_hrs" in update_data and update_data["time_hrs"] is not None:
            update_data["time_hrs"] = float(update_data["time_hrs"])
        
        update_data["updated_date"] = datetime.utcnow().isoformat()
        
        response = supabase.table(AppMmFocusSessionService.TABLE_NAME).update(update_data).eq("guid", str(focus_session_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmFocusSessionResponse(**response.data[0])
    
    @staticmethod
    def delete_focus_session(focus_session_id: UUID) -> bool:
        """Delete focus session by GUID"""
        response = supabase.table(AppMmFocusSessionService.TABLE_NAME).delete().eq("guid", str(focus_session_id)).execute()
        
        return len(response.data) > 0
