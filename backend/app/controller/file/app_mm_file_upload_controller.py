from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from typing import List
from model.file.app_mm_file_upload import AppMmFileUploadCreate, AppMmFileUploadUpdate, AppMmFileUploadResponse
from service.file.app_mm_file_upload_service import AppMmFileUploadService
from model.api_response import ApiResponse

router = APIRouter(prefix="/file-uploads", tags=["file-uploads"])

@router.post("/create", response_model=ApiResponse[AppMmFileUploadResponse], status_code=status.HTTP_201_CREATED)
def create_file_upload(file: AppMmFileUploadCreate):
    """Create a new file upload record"""
    try:
        result = AppMmFileUploadService.create_file_upload(file)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})

@router.get("/get-by-guid/{file_id}", response_model=ApiResponse[AppMmFileUploadResponse])
def get_file_upload(file_id: UUID):
    """Get file upload by ID"""
    file = AppMmFileUploadService.get_file_upload_by_id(file_id)
    if not file:
        return ApiResponse.error({"message": "File upload not found"})
    return ApiResponse.success(file)

@router.get("/get-all", response_model=ApiResponse[List[AppMmFileUploadResponse]])
def get_all_file_uploads():
    """Get all file uploads"""
    files = AppMmFileUploadService.get_all_file_uploads()
    return ApiResponse.success(files)

@router.get("/get-by-user/{user_guid}", response_model=ApiResponse[List[AppMmFileUploadResponse]])
def get_files_by_user(user_guid: UUID):
    """Get all files for a specific user"""
    files = AppMmFileUploadService.get_files_by_user(user_guid)
    return ApiResponse.success(files)

@router.get("/get-by-mime-type/{mime_type}", response_model=ApiResponse[List[AppMmFileUploadResponse]])
def get_files_by_mime_type(mime_type: str):
    """Get all files by mime type"""
    files = AppMmFileUploadService.get_files_by_mime_type(mime_type)
    return ApiResponse.success(files)

@router.put("/update/{file_id}", response_model=ApiResponse[AppMmFileUploadResponse])
def update_file_upload(file_id: UUID, file: AppMmFileUploadUpdate):
    """Update file upload by ID"""
    updated_file = AppMmFileUploadService.update_file_upload(file_id, file)
    if not updated_file:
        return ApiResponse.error({"message": "File upload not found"})
    return ApiResponse.success(updated_file)

@router.delete("/delete-by-guid/{file_id}", response_model=ApiResponse[dict])
def delete_file_upload(file_id: UUID):
    """Delete file upload by ID"""
    success = AppMmFileUploadService.delete_file_upload(file_id)
    if not success:
        return ApiResponse.error({"message": "File upload not found"})
    return ApiResponse.success({"message": "File upload deleted successfully"})
