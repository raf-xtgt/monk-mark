from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from typing import List
from model.library.app_mm_library_hdr import AppMmLibraryHdrCreate, AppMmLibraryHdrUpdate, AppMmLibraryHdrResponse, AppMmLibraryHdrWithFileResponse
from service.library.app_mm_library_hdr_service import AppMmLibraryHdrService
from service.library.book_search_service import BookSearchService
from model.api_response import ApiResponse
from model.dto.book_search_dto import BookSearchRequestDto, BookSearchResponseDto
from model.dto.app_mm_library_hdr_query_criteria import LibraryHdrQueryCriteria

router = APIRouter(prefix="/librarys", tags=["library"])

@router.post("/create", response_model=ApiResponse[AppMmLibraryHdrResponse], status_code=status.HTTP_201_CREATED)
def create_library_hdr(library_hdr: AppMmLibraryHdrCreate):
    """Create a new library header"""
    try:
        result = AppMmLibraryHdrService.create_library_hdr(library_hdr)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})

@router.get("/get-by-guid/{library_hdr_id}", response_model=ApiResponse[AppMmLibraryHdrResponse])
def get_library_hdr(library_hdr_id: UUID):
    """Get library header by ID"""
    library_hdr = AppMmLibraryHdrService.get_library_hdr_by_id(library_hdr_id)
    if not library_hdr:
        return ApiResponse.error({"message": "Library header not found"})
    return ApiResponse.success(library_hdr)

@router.get("/get-all", response_model=ApiResponse[List[AppMmLibraryHdrResponse]])
def get_all_library_hdrs():
    """Get all library headers"""
    libraries = AppMmLibraryHdrService.get_all_library_hdrs()
    return ApiResponse.success(libraries)

@router.get("/get-by-user/{user_guid}", response_model=ApiResponse[List[AppMmLibraryHdrResponse]])
def get_library_hdrs_by_user(user_guid: UUID):
    """Get all library headers for a specific user"""
    libraries = AppMmLibraryHdrService.get_library_hdrs_by_user(user_guid)
    return ApiResponse.success(libraries)

@router.put("/update/{library_hdr_id}", response_model=ApiResponse[AppMmLibraryHdrResponse])
def update_library_hdr(library_hdr_id: UUID, library_hdr: AppMmLibraryHdrUpdate):
    """Update library header by ID"""
    updated_library_hdr = AppMmLibraryHdrService.update_library_hdr(library_hdr_id, library_hdr)
    if not updated_library_hdr:
        return ApiResponse.error({"message": "Library header not found"})
    return ApiResponse.success(updated_library_hdr)

@router.put("/update-last-read/{library_hdr_id}", response_model=ApiResponse[AppMmLibraryHdrResponse])
def update_last_read_library_hdr(library_hdr_id: UUID):
    """Update last read time of the library"""
    updated_library_hdr = AppMmLibraryHdrService.update_last_read(library_hdr_id)
    if not updated_library_hdr:
        return ApiResponse.error({"message": "Library header not found"})
    return ApiResponse.success(updated_library_hdr)

@router.delete("/delete-by-guid/{library_hdr_id}", response_model=ApiResponse[dict])
def delete_library_hdr(library_hdr_id: UUID):
    """Delete library header by ID"""
    success = AppMmLibraryHdrService.delete_library_hdr(library_hdr_id)
    if not success:
        return ApiResponse.error({"message": "Library header not found"})
    return ApiResponse.success({"message": "Library header deleted successfully"})

@router.post("/search-book", response_model=ApiResponse)
def search_library_hdr(searchDto: BookSearchRequestDto):
    """
    Search for a book by name. First checks local database, then Google Books API.
    
    If no records found locally:
    - Uses Google Books API to fetch book information
    - Downloads and stores book cover in Supabase storage
    - Creates record in app_mm_file_upload
    - Creates record in app_mm_library_hdr with file_guid reference
    
    If record exists locally:
    - Retrieves file info using file_guid
    - Returns book cover URL from storage
    
    Input: Book name (e.g., "Deep Work") and user_guid
    Output: Book cover image URL, description, and author name
    """
    try:
        result = BookSearchService.search_book(searchDto.book_name, searchDto.user_guid)
        
        if not result:
            return ApiResponse.error({"message": f"Book '{searchDto.book_name}' not found"})
        
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": f"Error searching for book: {str(e)}"})


@router.post("/get-by-criteria", status_code=status.HTTP_201_CREATED)
def get_library_by_criteria(query_criteria: LibraryHdrQueryCriteria):
    """Get library hdrs by criteria with file storage path, ordered by last_read descending"""
    try:
        libraries = AppMmLibraryHdrService.get_library_hdrs_by_criteria(
            guid=query_criteria.guid,
            user_guid=query_criteria.user_guid,
            book_name=query_criteria.book_name
        )
        return ApiResponse.success(libraries)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})

@router.post("/search-and-get-by-criteria", status_code=status.HTTP_201_CREATED)
def search_and_get_by_criteria(query_criteria: LibraryHdrQueryCriteria):
    """Search for a book (local DB or Google Books API) then return enriched library data.
    
    Combines search-book and get-by-criteria:
    1. Uses BookSearchService to find or create the book if not in DB.
    2. Returns the full enriched response with storage paths and focus session stats.
    """
    try:
        libraries = AppMmLibraryHdrService.search_and_get_by_criteria(
            guid=query_criteria.guid,
            user_guid=query_criteria.user_guid,
            book_name=query_criteria.book_name
        )
        return ApiResponse.success(libraries)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})
