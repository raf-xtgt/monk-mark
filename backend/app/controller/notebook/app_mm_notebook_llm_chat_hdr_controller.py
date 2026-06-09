from fastapi import APIRouter, status
from uuid import UUID
from typing import List
from model.notebook.app_mm_notebook_llm_chat_hdr import (
    AppMmNotebookLlmChatHdrCreate,
    AppMmNotebookLlmChatHdrUpdate,
    AppMmNotebookLlmChatHdrResponse
)
from service.notebook.app_mm_notebook_llm_chat_hdr_service import NotebookLlmChatHdrService
from model.api_response import ApiResponse

router = APIRouter(prefix="/notebook-llm-chat-hdrs", tags=["notebook-llm-chat-hdrs"])

@router.post("/create", response_model=ApiResponse[AppMmNotebookLlmChatHdrResponse], status_code=status.HTTP_201_CREATED)
def create_chat_hdr(chat_hdr: AppMmNotebookLlmChatHdrCreate):
    """Create a new notebook LLM chat header"""
    try:
        result = NotebookLlmChatHdrService.create_chat_hdr(chat_hdr)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})

@router.get("/get-by-guid/{chat_hdr_id}", response_model=ApiResponse[AppMmNotebookLlmChatHdrResponse])
def get_chat_hdr(chat_hdr_id: UUID):
    """Get notebook LLM chat header by ID"""
    chat_hdr = NotebookLlmChatHdrService.get_chat_hdr_by_id(chat_hdr_id)
    if not chat_hdr:
        return ApiResponse.error({"message": "Notebook LLM chat header not found"})
    return ApiResponse.success(chat_hdr)

@router.get("/get-all", response_model=ApiResponse[List[AppMmNotebookLlmChatHdrResponse]])
def get_all_chat_hdrs():
    """Get all notebook LLM chat headers"""
    chat_hdrs = NotebookLlmChatHdrService.get_all_chat_hdrs()
    return ApiResponse.success(chat_hdrs)

@router.get("/get-by-user/{user_guid}", response_model=ApiResponse[List[AppMmNotebookLlmChatHdrResponse]])
def get_chat_hdrs_by_user(user_guid: UUID):
    """Get all notebook LLM chat headers for a specific user"""
    chat_hdrs = NotebookLlmChatHdrService.get_chat_hdrs_by_user(user_guid)
    return ApiResponse.success(chat_hdrs)

@router.get("/get-by-notebook/{notebook_hdr_guid}", response_model=ApiResponse[List[AppMmNotebookLlmChatHdrResponse]])
def get_chat_hdrs_by_notebook(notebook_hdr_guid: UUID):
    """Get all notebook LLM chat headers for a specific notebook"""
    chat_hdrs = NotebookLlmChatHdrService.get_chat_hdrs_by_notebook(notebook_hdr_guid)
    return ApiResponse.success(chat_hdrs)

@router.get("/get-by-library/{library_hdr_guid}", response_model=ApiResponse[List[AppMmNotebookLlmChatHdrResponse]])
def get_chat_hdrs_by_library(library_hdr_guid: UUID):
    """Get all notebook LLM chat headers for a specific library"""
    chat_hdrs = NotebookLlmChatHdrService.get_chat_hdrs_by_library(library_hdr_guid)
    return ApiResponse.success(chat_hdrs)

@router.put("/update/{chat_hdr_id}", response_model=ApiResponse[AppMmNotebookLlmChatHdrResponse])
def update_chat_hdr(chat_hdr_id: UUID, chat_hdr: AppMmNotebookLlmChatHdrUpdate):
    """Update notebook LLM chat header by ID"""
    updated_chat_hdr = NotebookLlmChatHdrService.update_chat_hdr(chat_hdr_id, chat_hdr)
    if not updated_chat_hdr:
        return ApiResponse.error({"message": "Notebook LLM chat header not found"})
    return ApiResponse.success(updated_chat_hdr)

@router.delete("/delete-by-guid/{chat_hdr_id}", response_model=ApiResponse[dict])
def delete_chat_hdr(chat_hdr_id: UUID):
    """Delete notebook LLM chat header by ID"""
    success = NotebookLlmChatHdrService.delete_chat_hdr(chat_hdr_id)
    if not success:
        return ApiResponse.error({"message": "Notebook LLM chat header not found"})
    return ApiResponse.success({"message": "Notebook LLM chat header deleted successfully"})
