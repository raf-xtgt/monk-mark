from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from typing import List, Union
from model.notebook.app_mm_notebook_hdr import AppMmNotebookHdrCreate, AppMmNotebookHdrUpdate, AppMmNotebookHdrResponse
from service.notebook.app_mm_notebook_hdr_service import AppMmNotebookHdrService
from model.api_response import ApiResponse

router = APIRouter(prefix="/notebooks", tags=["notebook"])

@router.post("/create", response_model=ApiResponse[AppMmNotebookHdrResponse], status_code=status.HTTP_201_CREATED)
def create_notebook_hdr(notebook_hdr: AppMmNotebookHdrCreate):
    """Create a new notebook header"""
    try:
        result = AppMmNotebookHdrService.create_notebook_hdr(notebook_hdr)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})

@router.get("/get-by-guid/{notebook_hdr_id}", response_model=ApiResponse[AppMmNotebookHdrResponse])
def get_notebook_hdr(notebook_hdr_id: UUID):
    """Get notebook header by ID"""
    notebook_hdr = AppMmNotebookHdrService.get_notebook_hdr_by_id(notebook_hdr_id)
    if not notebook_hdr:
        return ApiResponse.error({"message": "Notebook header not found"})
    return ApiResponse.success(notebook_hdr)

@router.get("/get-all", response_model=ApiResponse[List[AppMmNotebookHdrResponse]])
def get_all_notebook_hdrs():
    """Get all notebook headers"""
    notebooks = AppMmNotebookHdrService.get_all_notebook_hdrs()
    return ApiResponse.success(notebooks)

@router.get("/get-by-user/{user_guid}", response_model=ApiResponse[List[AppMmNotebookHdrResponse]])
def get_notebook_hdrs_by_user(user_guid: UUID):
    """Get all notebook headers for a specific user"""
    notebooks = AppMmNotebookHdrService.get_notebook_hdrs_by_user(user_guid)
    return ApiResponse.success(notebooks)

@router.get("/get-by-library/{library_hdr_guid}", response_model=ApiResponse[Union[AppMmNotebookHdrResponse, dict]])
def get_notebook_hdrs_by_library(library_hdr_guid: UUID):
    """Get first notebook header for a specific library"""
    notebook = AppMmNotebookHdrService.get_notebook_hdrs_by_library(library_hdr_guid)
    if not notebook:
        return ApiResponse.error({"message": "NOTEBOOK_HDR_BY_LIBRARY_NOT_FOUND"})
    return ApiResponse.success(notebook)

@router.put("/update/{notebook_hdr_id}", response_model=ApiResponse[AppMmNotebookHdrResponse])
def update_notebook_hdr(notebook_hdr_id: UUID, notebook_hdr: AppMmNotebookHdrUpdate):
    """Update notebook header by ID"""
    updated_notebook_hdr = AppMmNotebookHdrService.update_notebook_hdr(notebook_hdr_id, notebook_hdr)
    if not updated_notebook_hdr:
        return ApiResponse.error({"message": "Notebook header not found"})
    return ApiResponse.success(updated_notebook_hdr)

@router.delete("/delete-by-guid/{notebook_hdr_id}", response_model=ApiResponse[dict])
def delete_notebook_hdr(notebook_hdr_id: UUID):
    """Delete notebook header by ID"""
    success = AppMmNotebookHdrService.delete_notebook_hdr(notebook_hdr_id)
    if not success:
        return ApiResponse.error({"message": "Notebook header not found"})
    return ApiResponse.success({"message": "Notebook header deleted successfully"})
