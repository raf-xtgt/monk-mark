from fastapi import APIRouter, status, UploadFile, File, Form
from uuid import UUID, uuid4
from typing import List, Optional
import os
from model.notebook.app_mm_notebook_content_file_link import (
    AppMmNotebookContentFileLinkCreate,
    AppMmNotebookContentFileLinkUpdate,
    AppMmNotebookContentFileLinkResponse
)
from model.file.app_mm_file_upload import AppMmFileUploadCreate
from service.notebook.app_mm_notebook_content_file_link_service import NotebookContentFileLinkService
from service.file.app_mm_file_upload_service import AppMmFileUploadService
from util.supabase_config import supabase_admin
from model.api_response import ApiResponse
from model.dto.note_taking_dto import NoteTakingAgentRequest
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/notebook-content-file-links", tags=["notebook-content-file-links"])

@router.post("/create", response_model=ApiResponse[AppMmNotebookContentFileLinkResponse], status_code=status.HTTP_201_CREATED)
def create_link(link: AppMmNotebookContentFileLinkCreate):
    """Create a new notebook content file link"""
    try:
        result = NotebookContentFileLinkService.create(link)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})

@router.get("/get-by-guid/{link_id}", response_model=ApiResponse[AppMmNotebookContentFileLinkResponse])
def get_link(link_id: UUID):
    """Get notebook content file link by GUID"""
    link = NotebookContentFileLinkService.get_by_guid(link_id)
    if not link:
        return ApiResponse.error({"message": "Notebook content file link not found"})
    return ApiResponse.success(link)

@router.get("/get-all", response_model=ApiResponse[List[AppMmNotebookContentFileLinkResponse]])
def get_all_links():
    """Get all notebook content file links"""
    links = NotebookContentFileLinkService.get_all()
    return ApiResponse.success(links)

@router.get("/get-by-user/{user_guid}", response_model=ApiResponse[List[AppMmNotebookContentFileLinkResponse]])
def get_links_by_user(user_guid: UUID):
    """Get all notebook content file links by user GUID"""
    links = NotebookContentFileLinkService.get_by_user(user_guid)
    return ApiResponse.success(links)

@router.get("/get-by-notebook-hdr/{notebook_hdr_guid}", response_model=ApiResponse[List[AppMmNotebookContentFileLinkResponse]])
def get_links_by_notebook_hdr(notebook_hdr_guid: UUID):
    """Get all notebook content file links by notebook header GUID"""
    links = NotebookContentFileLinkService.get_by_notebook_hdr(notebook_hdr_guid)
    return ApiResponse.success(links)

@router.get("/get-by-notebook-content/{notebook_content_guid}", response_model=ApiResponse[List[AppMmNotebookContentFileLinkResponse]])
def get_links_by_notebook_content(notebook_content_guid: UUID):
    """Get all notebook content file links by notebook content GUID"""
    links = NotebookContentFileLinkService.get_by_notebook_content(notebook_content_guid)
    return ApiResponse.success(links)

@router.get("/get-by-file-upload/{file_upload_guid}", response_model=ApiResponse[List[AppMmNotebookContentFileLinkResponse]])
def get_links_by_file_upload(file_upload_guid: UUID):
    """Get all notebook content file links by file upload GUID"""
    links = NotebookContentFileLinkService.get_by_file_upload(file_upload_guid)
    return ApiResponse.success(links)

@router.put("/update/{link_id}", response_model=ApiResponse[AppMmNotebookContentFileLinkResponse])
def update_link(link_id: UUID, link: AppMmNotebookContentFileLinkUpdate):
    """Update notebook content file link by GUID"""
    updated_link = NotebookContentFileLinkService.update(link_id, link)
    if not updated_link:
        return ApiResponse.error({"message": "Notebook content file link not found"})
    return ApiResponse.success(updated_link)

@router.delete("/delete-by-guid/{link_id}", response_model=ApiResponse[dict])
def delete_link(link_id: UUID):
    """Delete notebook content file link by GUID"""
    success = NotebookContentFileLinkService.delete_by_guid(link_id)
    if not success:
        return ApiResponse.error({"message": "Notebook content file link not found"})
    return ApiResponse.success({"message": "Notebook content file link deleted successfully"})


@router.post("/upload-file", response_model=ApiResponse[AppMmNotebookContentFileLinkResponse], status_code=status.HTTP_201_CREATED)
async def upload_notebook_content_file(
    file: UploadFile = File(...),
    user_guid: str = Form(...),
    notebook_hdr_guid: str = Form(...),
    notebook_content_guid: Optional[str] = Form(None),
    highlight_metadata: Optional[str] = Form(None)
):
    """
    Upload a file to Supabase storage and create records in app_mm_file_upload 
    and app_mm_notebook_content_file_link
    """
    try:
        # Get environment variables
        storage_bucket = os.environ.get("SUPABASE_STORAGE_BUCKET")
        storage_folder = os.environ.get("SUPABASE_STORAGE_FOLDER_NOTEBOOK_CONTENT")
        
        if not storage_bucket or not storage_folder:
            return ApiResponse.error({"message": "Storage configuration missing"})
        
        # Read file content
        file_content = await file.read()
        
        # Determine file extension from content type or filename
        content_type = file.content_type or "image/jpeg"
        extension = content_type.split("/")[-1]
        if extension not in ["jpeg", "jpg", "png", "webp", "gif"]:
            # Try to get extension from filename
            if file.filename and "." in file.filename:
                extension = file.filename.split(".")[-1]
            else:
                extension = "jpg"
        
        # Generate unique filename
        filename = f"notebook_content_{uuid4()}.{extension}"
        storage_path = f"{storage_folder}/{filename}"
        
        # Upload to Supabase storage using admin client (bypasses RLS)
        supabase_admin.storage.from_(storage_bucket).upload(
            storage_path,
            file_content,
            {"content-type": content_type}
        )
        
        # Get public URL for the uploaded file
        public_url = supabase_admin.storage.from_(storage_bucket).get_public_url(storage_path)
        
        # Parse highlight_metadata if provided (expecting JSON string)
        metadata_dict = None
        if highlight_metadata:
            import json
            try:
                metadata_dict = json.loads(highlight_metadata)
            except json.JSONDecodeError:
                pass
        
        # Create file upload record
        file_create = AppMmFileUploadCreate(
            user_guid=UUID(user_guid),
            file_name=filename,
            mime_type=content_type,
            storage_path=storage_path,
            bucket_name=storage_bucket,
            is_public=True,
            metadata={
                "source": "notebook_content",
                "original_filename": file.filename,
                "notebook_hdr_guid": notebook_hdr_guid
            }
        )
        
        file_record = AppMmFileUploadService.create_file_upload(file_create)
        
        # Create notebook content file link record
        link_create = AppMmNotebookContentFileLinkCreate(
            user_guid=UUID(user_guid),
            notebook_hdr_guid=UUID(notebook_hdr_guid),
            notebook_content_guid=UUID(notebook_content_guid) if notebook_content_guid else None,
            file_upload_guid=file_record.guid,
            image_url=public_url,
            highlight_metadata=metadata_dict
        )
        
        link_record = NotebookContentFileLinkService.create(link_create)
        
        return ApiResponse.success(link_record)
        
    except Exception as e:
        return ApiResponse.error({"message": f"Failed to upload file: {str(e)}"})

@router.get("/get-attachment-by-content/{content_guid}", response_model=ApiResponse[List[dict]])
def get_file_attachment_by_content(content_guid: UUID):
    """Get file attachments with public URLs and highlight metadata for a specific notebook content"""
    try:
        # Get all file links for this content
        file_links = NotebookContentFileLinkService.get_by_notebook_content(content_guid)
        
        if not file_links:
            return ApiResponse.success([])
        
        # Create a mapping of file_upload_guid to file_link for quick lookup
        file_link_map = {str(link.file_upload_guid): link for link in file_links if link.file_upload_guid}
        
        # Collect all file_upload_guids
        file_upload_guids = [link.file_upload_guid for link in file_links if link.file_upload_guid]
        
        if not file_upload_guids:
            return ApiResponse.success([])
        
        # Fetch file upload records
        from util.supabase_config import supabase
        file_response = supabase.table("app_mm_file_upload").select("guid, storage_path, bucket_name").in_("guid", [str(guid) for guid in file_upload_guids]).execute()
        
        if not file_response.data:
            return ApiResponse.success([])
        
        # Build result with public URLs and highlight metadata
        result = []
        for file_record in file_response.data:
            try:
                # Get public URL from Supabase storage
                public_url = supabase.storage.from_(file_record["bucket_name"]).get_public_url(file_record["storage_path"])
                
                # Get the corresponding file_link to retrieve highlight_metadata
                file_link = file_link_map.get(file_record["guid"])
                
                result.append({
                    "content_guid": str(content_guid),
                    "file_path": public_url,
                    "highlight_metadata": file_link.highlight_metadata if file_link else None
                })
            except Exception as e:
                print(f"Error getting public URL for {file_record['guid']}: {str(e)}")
                # Skip files that fail to get public URL
                continue
        
        return ApiResponse.success(result)
        
    except Exception as e:
        return ApiResponse.error({"message": f"Failed to get attachments: {str(e)}"})


@router.post("/trigger-and-store-note-taking", response_model=ApiResponse[dict], status_code=status.HTTP_200_OK)
async def trigger_and_store_note_taking(request: NoteTakingAgentRequest):
    """Trigger the note-taking agent with a highlighted image and store the result.

    Renders highlight overlays onto the specified image, passes it to the
    note-taking agent for OCR/comprehension, and updates the notebook content
    record with the generated note.
    """
    try:
        result = await NotebookContentFileLinkService.trigger_and_store_note(
            notebook_hdr_guid=request.notebook_hdr_guid,
            notebook_content_guid=request.notebook_content_guid,
            image_url=request.image_url,
            highlight_metadata=request.highlight_metadata,
        )

        if result.get("status") == "error":
            return ApiResponse.error({"message": result.get("message", "Unknown error")})

        return ApiResponse.success(result)

    except Exception as e:
        return ApiResponse.error({"message": f"Failed to trigger note-taking agent: {str(e)}"})