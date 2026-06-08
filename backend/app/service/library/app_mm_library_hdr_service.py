from uuid import UUID, uuid4
from typing import List, Optional
from util.supabase_config import supabase
from model.library.app_mm_library_hdr import AppMmLibraryHdrCreate, AppMmLibraryHdrUpdate, AppMmLibraryHdrResponse, AppMmLibraryHdrWithFileResponse

class AppMmLibraryHdrService:
    TABLE_NAME = "app_mm_library_hdr"
    FILE_UPLOAD_TABLE = "app_mm_file_upload"
    FOCUS_SESSION_TABLE = "app_mm_focus_session"
    
    @staticmethod
    def create_library_hdr(library_hdr_data: AppMmLibraryHdrCreate) -> AppMmLibraryHdrResponse:
        """Create a new library header"""
        new_library_hdr = {
            "guid": str(uuid4()),
            "user_guid": str(library_hdr_data.user_guid),
            "book_name": library_hdr_data.book_name,
            "book_desc": library_hdr_data.book_desc,
            "file_guid": str(library_hdr_data.file_guid) if library_hdr_data.file_guid else None
        }
        
        response = supabase.table(AppMmLibraryHdrService.TABLE_NAME).insert(new_library_hdr).execute()
        
        if not response.data:
            raise Exception("Failed to create library header")
        
        return AppMmLibraryHdrResponse(**response.data[0])
    
    @staticmethod
    def get_library_hdr_by_id(library_hdr_id: UUID) -> Optional[AppMmLibraryHdrResponse]:
        """Get library header by GUID"""
        response = supabase.table(AppMmLibraryHdrService.TABLE_NAME).select("*").eq("guid", str(library_hdr_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmLibraryHdrResponse(**response.data[0])
    
    @staticmethod
    def get_all_library_hdrs() -> List[AppMmLibraryHdrResponse]:
        """Get all library headers"""
        response = supabase.table(AppMmLibraryHdrService.TABLE_NAME).select("*").execute()
        
        return [AppMmLibraryHdrResponse(**library_hdr) for library_hdr in response.data]
    
    @staticmethod
    def get_library_hdrs_by_user(user_guid: UUID) -> List[AppMmLibraryHdrResponse]:
        """Get all library headers for a specific user"""
        response = supabase.table(AppMmLibraryHdrService.TABLE_NAME).select("*").eq("user_guid", str(user_guid)).execute()
        
        return [AppMmLibraryHdrResponse(**library_hdr) for library_hdr in response.data]
    
    @staticmethod
    def update_library_hdr(library_hdr_id: UUID, library_hdr_data: AppMmLibraryHdrUpdate) -> Optional[AppMmLibraryHdrResponse]:
        """Update library header by GUID"""
        update_data = library_hdr_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return AppMmLibraryHdrService.get_library_hdr_by_id(library_hdr_id)
        
        # Convert UUID to string for Supabase
        if "file_guid" in update_data:
            update_data["file_guid"] = str(update_data["file_guid"]) if update_data["file_guid"] else None
        
        response = supabase.table(AppMmLibraryHdrService.TABLE_NAME).update(update_data).eq("guid", str(library_hdr_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmLibraryHdrResponse(**response.data[0])
    
    @staticmethod
    def update_last_read(library_hdr_id: UUID) -> Optional[AppMmLibraryHdrResponse]:
        """Update last_read timestamp to current time"""
        from datetime import datetime, timezone
        
        update_data = {
            "last_read": datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table(AppMmLibraryHdrService.TABLE_NAME).update(update_data).eq("guid", str(library_hdr_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmLibraryHdrResponse(**response.data[0])
    
    @staticmethod
    def delete_library_hdr(library_hdr_id: UUID) -> bool:
        """Delete library header by GUID"""
        response = supabase.table(AppMmLibraryHdrService.TABLE_NAME).delete().eq("guid", str(library_hdr_id)).execute()
        
        return len(response.data) > 0

    @staticmethod
    def get_library_hdrs_by_criteria(guid: Optional[UUID] = None, user_guid: Optional[UUID] = None, book_name: Optional[str] = None) -> List[AppMmLibraryHdrWithFileResponse]:
        """Get library headers by criteria with file storage path and focus session stats (manual join), ordered by last_read descending"""
        # First, query library headers with filters
        query = supabase.table(AppMmLibraryHdrService.TABLE_NAME).select("*")
        
        if guid:
            query = query.eq("guid", str(guid))
        if user_guid:
            query = query.eq("user_guid", str(user_guid))
        if book_name:
            query = query.ilike("book_name", f"%{book_name}%")
        
        # Order by last_read descending
        query = query.order("last_read", desc=True)
        
        library_response = query.execute()
        
        if not library_response.data:
            return []
        
        # Collect all library guids for focus session lookup
        library_guids = [item["guid"] for item in library_response.data]
        
        # Collect all unique file_guids that are not None
        file_guids = [item["file_guid"] for item in library_response.data if item.get("file_guid")]
        
        # Fetch file upload records if there are any file_guids
        file_map = {}
        if file_guids:
            file_response = supabase.table(AppMmLibraryHdrService.FILE_UPLOAD_TABLE).select("guid, storage_path, bucket_name").in_("guid", file_guids).execute()
            
            # Create a map of file_guid -> public URL
            for file_record in file_response.data:
                try:
                    # Get public URL from Supabase storage
                    public_url = supabase.storage.from_(file_record["bucket_name"]).get_public_url(file_record["storage_path"])
                    file_map[file_record["guid"]] = public_url
                except Exception as e:
                    print(f"Error getting public URL for {file_record['guid']}: {str(e)}")
                    file_map[file_record["guid"]] = None
        
        # Fetch focus session stats
        focus_stats_map = {}
        if library_guids:
            focus_response = supabase.table(AppMmLibraryHdrService.FOCUS_SESSION_TABLE).select("library_hdr_guid, time_hrs, time_seconds").in_("library_hdr_guid", library_guids).execute()
            
            # Aggregate focus session data by library_hdr_guid
            for session in focus_response.data:
                lib_guid = session["library_hdr_guid"]
                if lib_guid not in focus_stats_map:
                    focus_stats_map[lib_guid] = {
                        "count": 0,
                        "total_hrs": 0.0,
                        "total_seconds": 0
                    }
                
                focus_stats_map[lib_guid]["count"] += 1
                
                # Add time_hrs (convert from Decimal/string to float)
                if session.get("time_hrs"):
                    try:
                        focus_stats_map[lib_guid]["total_hrs"] += float(session["time_hrs"])
                    except (ValueError, TypeError):
                        pass
                
                # Add time_seconds
                if session.get("time_seconds"):
                    focus_stats_map[lib_guid]["total_seconds"] += int(session["time_seconds"])
        
        # Combine the data
        result = []
        for item in library_response.data:
            lib_guid = item["guid"]
            file_guid = item.get("file_guid")
            storage_path = file_map.get(file_guid) if file_guid else None
            
            # Get focus session stats
            focus_stats = focus_stats_map.get(lib_guid, {"count": 0, "total_hrs": 0.0, "total_seconds": 0})
            
            # Calculate total time focused
            total_seconds = focus_stats["total_seconds"]
            total_hrs_from_seconds = total_seconds / 3600.0
            total_hrs = focus_stats["total_hrs"] + total_hrs_from_seconds
            
            # Convert to hours and minutes
            time_focused_hrs = int(total_hrs)
            time_focused_minutes = int((total_hrs - time_focused_hrs) * 60)
            
            # Format focus_time as "00h 00min"
            focus_time = f"{time_focused_hrs}h {time_focused_minutes}min"
            
            library_data = {
                "guid": item["guid"],
                "user_guid": item["user_guid"],
                "book_name": item["book_name"],
                "book_desc": "",
                "file_guid": item["file_guid"],
                "created_date": item["created_date"],
                "last_read": item["last_read"],
                "storage_path": storage_path,
                "session_count": focus_stats["count"],
                "time_focused_hrs": time_focused_hrs,
                "time_focused_minutes": time_focused_minutes,
                "focus_time": focus_time
            }
            result.append(AppMmLibraryHdrWithFileResponse(**library_data))
        
        return result

    @staticmethod
    def search_and_get_by_criteria(guid: Optional[UUID] = None, user_guid: Optional[UUID] = None, book_name: Optional[str] = None) -> List[AppMmLibraryHdrWithFileResponse]:
        """Search for a book (local DB or Google Books API) then return enriched library data.
        
        Combines the search_book flow with the get_library_hdrs_by_criteria enrichment:
        1. If book_name is provided, use BookSearchService.search_book to find or create the book.
        2. Then query the database using the same criteria logic as get_library_hdrs_by_criteria
           to return the full enriched response with storage paths and focus session stats.
        """
        from service.library.book_search_service import BookSearchService

        # Step 1: If book_name and user_guid are provided, ensure the book exists via search
        if book_name and user_guid:
            BookSearchService.search_book(book_name, user_guid)

        # Step 2: Query library headers with filters (same logic as get_library_hdrs_by_criteria)
        query = supabase.table(AppMmLibraryHdrService.TABLE_NAME).select("*")

        if guid:
            query = query.eq("guid", str(guid))
        if user_guid:
            query = query.eq("user_guid", str(user_guid))
        if book_name:
            query = query.ilike("book_name", f"%{book_name}%")

        query = query.order("last_read", desc=True)

        library_response = query.execute()

        if not library_response.data:
            return []

        # Step 3: Enrich with file URLs and focus session stats
        library_guids = [item["guid"] for item in library_response.data]
        file_guids = [item["file_guid"] for item in library_response.data if item.get("file_guid")]

        # Fetch file upload records
        file_map = {}
        if file_guids:
            file_response = supabase.table(AppMmLibraryHdrService.FILE_UPLOAD_TABLE).select("guid, storage_path, bucket_name").in_("guid", file_guids).execute()

            for file_record in file_response.data:
                try:
                    public_url = supabase.storage.from_(file_record["bucket_name"]).get_public_url(file_record["storage_path"])
                    file_map[file_record["guid"]] = public_url
                except Exception as e:
                    print(f"Error getting public URL for {file_record['guid']}: {str(e)}")
                    file_map[file_record["guid"]] = None

        # Fetch focus session stats
        focus_stats_map = {}
        if library_guids:
            focus_response = supabase.table(AppMmLibraryHdrService.FOCUS_SESSION_TABLE).select("library_hdr_guid, time_hrs, time_seconds").in_("library_hdr_guid", library_guids).execute()

            for session in focus_response.data:
                lib_guid = session["library_hdr_guid"]
                if lib_guid not in focus_stats_map:
                    focus_stats_map[lib_guid] = {
                        "count": 0,
                        "total_hrs": 0.0,
                        "total_seconds": 0
                    }

                focus_stats_map[lib_guid]["count"] += 1

                if session.get("time_hrs"):
                    try:
                        focus_stats_map[lib_guid]["total_hrs"] += float(session["time_hrs"])
                    except (ValueError, TypeError):
                        pass

                if session.get("time_seconds"):
                    focus_stats_map[lib_guid]["total_seconds"] += int(session["time_seconds"])

        # Step 4: Build response
        result = []
        for item in library_response.data:
            lib_guid = item["guid"]
            file_guid = item.get("file_guid")
            storage_path = file_map.get(file_guid) if file_guid else None

            focus_stats = focus_stats_map.get(lib_guid, {"count": 0, "total_hrs": 0.0, "total_seconds": 0})

            total_seconds = focus_stats["total_seconds"]
            total_hrs_from_seconds = total_seconds / 3600.0
            total_hrs = focus_stats["total_hrs"] + total_hrs_from_seconds

            time_focused_hrs = int(total_hrs)
            time_focused_minutes = int((total_hrs - time_focused_hrs) * 60)
            focus_time = f"{time_focused_hrs}h {time_focused_minutes}min"

            library_data = {
                "guid": item["guid"],
                "user_guid": item["user_guid"],
                "book_name": item["book_name"],
                "book_desc": "",
                "file_guid": item["file_guid"],
                "created_date": item["created_date"],
                "last_read": item["last_read"],
                "storage_path": storage_path,
                "session_count": focus_stats["count"],
                "time_focused_hrs": time_focused_hrs,
                "time_focused_minutes": time_focused_minutes,
                "focus_time": focus_time
            }
            result.append(AppMmLibraryHdrWithFileResponse(**library_data))

        return result

    @staticmethod
    def get_book_title(library_hdr_guid: UUID) -> Optional[str]:
        """Get the book title for a given library header GUID.

        Args:
            library_hdr_guid: The UUID of the library header record.

        Returns:
            The book_name string if found, otherwise None.
        """
        response = (
            supabase.table(AppMmLibraryHdrService.TABLE_NAME)
            .select("book_name")
            .eq("guid", str(library_hdr_guid))
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0].get("book_name")