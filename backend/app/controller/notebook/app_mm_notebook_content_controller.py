from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from typing import List
from model.notebook.app_mm_notebook_content import AppMmNotebookContentCreate, AppMmNotebookContentUpdate, AppMmNotebookContentResponse
from service.notebook.app_mm_notebook_content_service import AppMmNotebookContentService
from model.api_response import ApiResponse

router = APIRouter(prefix="/notebook-contents", tags=["notebook-contents"])

@router.post("/create", response_model=ApiResponse[AppMmNotebookContentResponse], status_code=status.HTTP_201_CREATED)
def create_notebook_content(content: AppMmNotebookContentCreate):
    """Create a new notebook content entry"""
    try:
        result = AppMmNotebookContentService.create_notebook_content(content)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})

@router.get("/get-by-guid/{content_id}", response_model=ApiResponse[AppMmNotebookContentResponse])
def get_notebook_content(content_id: UUID):
    """Get notebook content by ID"""
    content = AppMmNotebookContentService.get_notebook_content_by_id(content_id)
    if not content:
        return ApiResponse.error({"message": "Notebook content not found"})
    return ApiResponse.success(content)

@router.get("/get-all", response_model=ApiResponse[List[AppMmNotebookContentResponse]])
def get_all_notebook_contents():
    """Get all notebook contents"""
    contents = AppMmNotebookContentService.get_all_notebook_contents()
    return ApiResponse.success(contents)

@router.get("/get-by-notebook-hdr/{notebook_hdr_guid}", response_model=ApiResponse[List[AppMmNotebookContentResponse]])
def get_contents_by_notebook_hdr(notebook_hdr_guid: UUID):
    """Get all contents for a specific notebook header"""
    contents = AppMmNotebookContentService.get_contents_by_notebook_hdr(notebook_hdr_guid)
    return ApiResponse.success(contents)

@router.get("/get-by-user/{user_guid}", response_model=ApiResponse[List[AppMmNotebookContentResponse]])
def get_contents_by_user(user_guid: UUID):
    """Get all contents for a specific user"""
    contents = AppMmNotebookContentService.get_contents_by_user(user_guid)
    return ApiResponse.success(contents)

@router.put("/update/{content_id}", response_model=ApiResponse[AppMmNotebookContentResponse])
def update_notebook_content(content_id: UUID, content: AppMmNotebookContentUpdate):
    """Update notebook content by ID"""
    updated_content = AppMmNotebookContentService.update_notebook_content(content_id, content)
    if not updated_content:
        return ApiResponse.error({"message": "Notebook content not found"})
    return ApiResponse.success(updated_content)

@router.delete("/delete-by-guid/{content_id}", response_model=ApiResponse[dict])
def delete_notebook_content(content_id: UUID):
    """Delete notebook content by ID"""
    success = AppMmNotebookContentService.delete_notebook_content(content_id)
    if not success:
        return ApiResponse.error({"message": "Notebook content not found"})
    return ApiResponse.success({"message": "Notebook content deleted successfully"})

@router.post("/generate-test-data", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED)
def generate_test_notebook_contents():
    """Generate dummy notebook content data for testing the art generator agent."""
    from uuid import UUID as _UUID
    from model.dto.reward_simulation_dto import SIMULATION_TEST_NOTES

    user_guid = _UUID("69cdaaa7-9800-42d9-a4c4-23db3b685a2d")
    notebook_hdr_guid = _UUID("f28ede59-922b-4261-9e74-da6ff0d6e480")
    library_hdr_guid = _UUID("dede4054-06bb-41b6-bc03-ac74b241160e")

    try:
        created_count = 0
        for note in SIMULATION_TEST_NOTES:
            content = AppMmNotebookContentCreate(
                user_guid=user_guid,
                notebook_hdr_guid=notebook_hdr_guid,
                library_hdr_guid=library_hdr_guid,
                content_text=note["content_text"],
                sequence_no=note["sequence_no"],
            )
            AppMmNotebookContentService.create_notebook_content(content)
            created_count += 1

        return ApiResponse.success({
            "message": f"Created {created_count} test notebook contents",
            "user_guid": str(user_guid),
            "notebook_hdr_guid": str(notebook_hdr_guid),
            "library_hdr_guid": str(library_hdr_guid),
        })
    except Exception as e:
        return ApiResponse.error({"message": str(e)})