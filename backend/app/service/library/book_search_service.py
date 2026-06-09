import requests
import os
from uuid import UUID, uuid4
from typing import Optional, Dict, Any
from io import BytesIO
from util.supabase_config import supabase, supabase_admin
from service.library.app_mm_library_hdr_service import AppMmLibraryHdrService
from service.file.app_mm_file_upload_service import AppMmFileUploadService
from model.library.app_mm_library_hdr import AppMmLibraryHdrCreate
from model.file.app_mm_file_upload import AppMmFileUploadCreate
from model.dto.book_search_dto import BookSearchResponseDto
from dotenv import load_dotenv

load_dotenv()

class BookSearchService:
    GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
    STORAGE_BUCKET = os.environ.get("SUPABASE_STORAGE_BUCKET")
    STORAGE_FOLDER = os.environ.get("SUPABASE_STORAGE_FOLDER")
    
    @staticmethod
    def search_book(book_name: str, user_guid: UUID) -> Optional[BookSearchResponseDto]:
        """
        Search for a book by name. First checks local database, then Google Books API.
        """
        # Step 1: Search in local database
        existing_books = AppMmLibraryHdrService.get_library_hdrs_by_user(user_guid)
        for book in existing_books:
            if book.book_name.lower() == book_name.lower():
                # Found in database, retrieve file info if available
                cover_url = None
                if book.file_guid:
                    file_record = AppMmFileUploadService.get_file_upload_by_id(book.file_guid)
                    if file_record:
                        # Get public URL from Supabase storage
                        cover_url = BookSearchService._get_storage_public_url(
                            file_record.bucket_name, 
                            file_record.storage_path
                        )
                
                return BookSearchResponseDto(
                    guid=book.guid,
                    book_name=book.book_name,
                    author=None,  # Not stored in current schema
                    description=book.book_desc,
                    cover_image_url=cover_url,
                    file_guid=book.file_guid
                )
        
        # Step 2: Not found locally, search Google Books API
        google_book_data = BookSearchService._search_google_books(book_name)
        if not google_book_data:
            return None
        
        # Step 3: Download and store cover image if available
        file_guid = None
        cover_url = google_book_data.get("cover_url")
        
        if cover_url:
            file_guid = BookSearchService._download_and_store_cover(
                cover_url, 
                book_name, 
                user_guid
            )
        
        # Step 4: Create library record
        library_create = AppMmLibraryHdrCreate(
            user_guid=user_guid,
            book_name=google_book_data.get("title", book_name),
            book_desc=google_book_data.get("description"),
            file_guid=file_guid
        )
        
        library_record = AppMmLibraryHdrService.create_library_hdr(library_create)
        
        return BookSearchResponseDto(
            guid=library_record.guid,
            book_name=library_record.book_name,
            author=google_book_data.get("author"),
            description=library_record.book_desc,
            cover_image_url=cover_url,
            file_guid=file_guid
        )
    
    @staticmethod
    def _search_google_books(book_name: str) -> Optional[Dict[str, Any]]:
        """Search Google Books API for book information"""
        try:
            api_key = os.environ.get("MM_GOOGLE_BOOKS_API_KEY")
            
            # Log API key status (without exposing the actual key)
            if not api_key:
                print(f"[BookSearch] WARNING: GOOGLE_BOOKS_API_KEY not configured")
            else:
                print(f"[BookSearch] API key configured (length: {len(api_key)})")
            
            params = {"q": book_name, "maxResults": 1}
            if api_key:
                params["key"] = api_key
            
            print(f"[BookSearch] Sending request to Google Books API for: '{book_name}'")
            print(f"[BookSearch] Request URL: {BookSearchService.GOOGLE_BOOKS_API_URL}")
            
            response = requests.get(
                BookSearchService.GOOGLE_BOOKS_API_URL, 
                params=params, 
                timeout=10
            )
            
            print(f"[BookSearch] Response status: {response.status_code}")
            
            # Handle rate limiting specifically
            if response.status_code == 429:
                print(f"[BookSearch] ERROR: Rate limit exceeded. Consider:")
                return None
            
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("items"):
                print(f"[BookSearch] No results found for: '{book_name}'")
                return None
            
            print(f"[BookSearch] Found {len(data.get('items', []))} result(s)")
            
            book_info = data["items"][0]["volumeInfo"]
            
            # Extract cover image URL (prefer high quality)
            cover_url = None
            if "imageLinks" in book_info:
                cover_url = (
                    book_info["imageLinks"].get("large") or
                    book_info["imageLinks"].get("medium") or
                    book_info["imageLinks"].get("thumbnail")
                )
                print(f"[BookSearch] Cover image found: {cover_url is not None}")
            
            # Extract authors
            authors = book_info.get("authors", [])
            author_str = ", ".join(authors) if authors else None
            
            print(f"[BookSearch] Successfully retrieved: '{book_info.get('title')}' by {author_str}")
            
            return {
                "title": book_info.get("title"),
                "author": author_str,
                "description": book_info.get("description"),
                "cover_url": cover_url
            }
        
        except requests.exceptions.RequestException as e:
            print(f"[BookSearch] Request error: {str(e)}")
            return None
        except Exception as e:
            print(f"[BookSearch] Unexpected error: {str(e)}")
            return None
    
    @staticmethod
    def _download_and_store_cover(
        image_url: str, 
        book_name: str, 
        user_guid: UUID
    ) -> Optional[UUID]:
        """Download cover image and store in Supabase storage"""
        try:
            # Download image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Determine file extension from content type
            content_type = response.headers.get("content-type", "image/jpeg")
            extension = content_type.split("/")[-1]
            if extension not in ["jpeg", "jpg", "png", "webp"]:
                extension = "jpg"
            
            # Generate unique filename
            filename = f"{book_name.replace(' ', '_')}_{uuid4()}.{extension}"
            storage_path = f"{BookSearchService.STORAGE_FOLDER}/{filename}"
            
            # Upload to Supabase storage using admin client (bypasses RLS)
            supabase_admin.storage.from_(BookSearchService.STORAGE_BUCKET).upload(
                storage_path,
                response.content,
                {"content-type": content_type}
            )
            
            # Create file upload record
            file_create = AppMmFileUploadCreate(
                user_guid=user_guid,
                file_name=filename,
                mime_type=content_type,
                storage_path=storage_path,
                bucket_name=BookSearchService.STORAGE_BUCKET,
                is_public=True,
                metadata={"source": "google_books", "book_name": book_name}
            )
            
            file_record = AppMmFileUploadService.create_file_upload(file_create)
            return file_record.guid
        
        except Exception as e:
            print(f"Error downloading/storing cover image: {str(e)}")
            return None
    
    @staticmethod
    def _get_storage_public_url(bucket_name: str, storage_path: str) -> Optional[str]:
        """Get public URL for a file in Supabase storage"""
        try:
            result = supabase.storage.from_(bucket_name).get_public_url(storage_path)
            return result
        except Exception as e:
            print(f"Error getting public URL: {str(e)}")
            return None
