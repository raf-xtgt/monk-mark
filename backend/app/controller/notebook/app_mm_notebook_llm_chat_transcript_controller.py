from fastapi import APIRouter, status
from uuid import UUID
from typing import List
from model.notebook.app_mm_notebook_llm_chat_transcript import (
    AppMmNotebookLlmChatTranscriptCreate,
    AppMmNotebookLlmChatTranscriptUpdate,
    AppMmNotebookLlmChatTranscriptResponse
)
from model.dto.notebook_chat_transcript_dto import NotebookChatTranscriptDto
from service.notebook.app_mm_notebook_llm_chat_transcript_service import NotebookLlmChatTranscriptService
from model.api_response import ApiResponse
from model.dto.notebook_chat_transcript_response_dto import NotebookChatTranscriptResponseDto

router = APIRouter(prefix="/notebook-llm-chat-transcripts", tags=["notebook-llm-chat-transcripts"])

@router.post("/create", response_model=ApiResponse[AppMmNotebookLlmChatTranscriptResponse], status_code=status.HTTP_201_CREATED)
def create_transcript(transcript: AppMmNotebookLlmChatTranscriptCreate):
    """Create a new notebook LLM chat transcript"""
    try:
        result = NotebookLlmChatTranscriptService.create_transcript(transcript)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})

@router.get("/get-by-guid/{transcript_id}", response_model=ApiResponse[AppMmNotebookLlmChatTranscriptResponse])
def get_transcript(transcript_id: UUID):
    """Get notebook LLM chat transcript by ID"""
    transcript = NotebookLlmChatTranscriptService.get_transcript_by_id(transcript_id)
    if not transcript:
        return ApiResponse.error({"message": "Notebook LLM chat transcript not found"})
    return ApiResponse.success(transcript)

@router.get("/get-all", response_model=ApiResponse[List[AppMmNotebookLlmChatTranscriptResponse]])
def get_all_transcripts():
    """Get all notebook LLM chat transcripts"""
    transcripts = NotebookLlmChatTranscriptService.get_all_transcripts()
    return ApiResponse.success(transcripts)

@router.get("/get-by-user/{user_guid}", response_model=ApiResponse[List[AppMmNotebookLlmChatTranscriptResponse]])
def get_transcripts_by_user(user_guid: UUID):
    """Get all notebook LLM chat transcripts for a specific user"""
    transcripts = NotebookLlmChatTranscriptService.get_transcripts_by_user(user_guid)
    return ApiResponse.success(transcripts)

@router.get("/get-by-chat-hdr/{llm_chat_hdr_guid}", response_model=ApiResponse[List[AppMmNotebookLlmChatTranscriptResponse]])
def get_transcripts_by_chat_hdr(llm_chat_hdr_guid: UUID):
    """Get all notebook LLM chat transcripts for a specific chat header (ordered by created_date)"""
    transcripts = NotebookLlmChatTranscriptService.get_transcripts_by_chat_hdr(llm_chat_hdr_guid)
    return ApiResponse.success(transcripts)

@router.post("/get-by-notebook-hdr", response_model=ApiResponse[NotebookChatTranscriptResponseDto])
def get_transcripts_by_notebook(payload: NotebookChatTranscriptDto):
    """Get all notebook LLM chat transcripts for a specific notebook hdr"""
    from service.notebook.app_mm_notebook_llm_chat_hdr_service import NotebookLlmChatHdrService
    from model.notebook.app_mm_notebook_llm_chat_hdr import AppMmNotebookLlmChatHdrCreate
    from model.dto.notebook_chat_transcript_response_dto import NotebookChatTranscriptResponseDto
    
    # Check if notebook has any chat header record
    chat_hdrs = NotebookLlmChatHdrService.get_chat_hdrs_by_notebook(payload.notebook_hdr_guid)
    
    if not chat_hdrs:
        # No chat header exists, create one
        new_chat_hdr = AppMmNotebookLlmChatHdrCreate(
            user_guid=payload.user_guid,
            notebook_hdr_guid=payload.notebook_hdr_guid,
            library_hdr_guid=payload.library_hdr_guid
        )
        created_chat_hdr = NotebookLlmChatHdrService.create_chat_hdr(new_chat_hdr)
        chat_hdr_guid = created_chat_hdr.guid
        library_hdr_guid = created_chat_hdr.library_hdr_guid
    else:
        # Use the first chat header (assuming one chat header per notebook)
        chat_hdr_guid = chat_hdrs[0].guid
        library_hdr_guid = chat_hdrs[0].library_hdr_guid
    
    # Get transcripts for this chat header
    transcripts = NotebookLlmChatTranscriptService.get_transcripts_by_chat_hdr(chat_hdr_guid)
    
    # Construct the response DTO
    response = NotebookChatTranscriptResponseDto(
        chat_hdr_guid=chat_hdr_guid,
        library_hdr_guid=library_hdr_guid,
        chat_transcripts=transcripts
    )
    
    return ApiResponse.success(response)

@router.get("/count-by-notebook/{notebook_hdr_guid}", response_model=ApiResponse[dict])
def count_transcripts_by_notebook(notebook_hdr_guid: UUID):
    """Get the total count of transcripts for a given notebook_hdr_guid"""
    from service.notebook.app_mm_notebook_llm_chat_hdr_service import NotebookLlmChatHdrService

    try:
        chat_hdrs = NotebookLlmChatHdrService.get_chat_hdrs_by_notebook(notebook_hdr_guid)

        if not chat_hdrs:
            return ApiResponse.success({"notebook_hdr_guid": str(notebook_hdr_guid), "total_count": 0})

        total_count = 0
        for chat_hdr in chat_hdrs:
            total_count += NotebookLlmChatTranscriptService.count_transcripts_by_chat_hdr(chat_hdr.guid)

        return ApiResponse.success({"notebook_hdr_guid": str(notebook_hdr_guid), "total_count": total_count})
    except Exception as e:
        return ApiResponse.error({"message": str(e)})

@router.post("/generate-greeting", response_model=ApiResponse[AppMmNotebookLlmChatTranscriptResponse], status_code=status.HTTP_201_CREATED)
def generate_greeting(payload: NotebookChatTranscriptDto):
    """Generate and persist a greeting message as the first assistant message for a new chat session.

    Looks up the book title from library_hdr_guid and creates a short thematic
    greeting. The greeting is persisted to the transcript table and returned.
    """
    from service.notebook.app_mm_notebook_llm_chat_hdr_service import NotebookLlmChatHdrService
    from model.notebook.app_mm_notebook_llm_chat_hdr import AppMmNotebookLlmChatHdrCreate
    from service.library.app_mm_library_hdr_service import AppMmLibraryHdrService

    try:
        # Get or create chat header
        chat_hdrs = NotebookLlmChatHdrService.get_chat_hdrs_by_notebook(payload.notebook_hdr_guid)

        if not chat_hdrs:
            new_chat_hdr = AppMmNotebookLlmChatHdrCreate(
                user_guid=payload.user_guid,
                notebook_hdr_guid=payload.notebook_hdr_guid,
                library_hdr_guid=payload.library_hdr_guid
            )
            created_chat_hdr = NotebookLlmChatHdrService.create_chat_hdr(new_chat_hdr)
            chat_hdr_guid = created_chat_hdr.guid
        else:
            chat_hdr_guid = chat_hdrs[0].guid

        # Look up book title
        book_title = None
        if payload.library_hdr_guid:
            book_title = AppMmLibraryHdrService.get_book_title(payload.library_hdr_guid)

        # Generate greeting based on book title
        if book_title:
            greeting = f"Ready to explore \"{book_title}\" together. What's on your mind?"
        else:
            greeting = "Ready to dive into your reading. What's on your mind?"

        # Persist greeting as the first assistant message
        transcript_data = AppMmNotebookLlmChatTranscriptCreate(
            user_guid=payload.user_guid,
            llm_chat_hdr_guid=chat_hdr_guid,
            msg_content=greeting,
            sender="assistant",
        )
        result = NotebookLlmChatTranscriptService.create_transcript(transcript_data)
        return ApiResponse.success(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})


@router.put("/update/{transcript_id}", response_model=ApiResponse[AppMmNotebookLlmChatTranscriptResponse])
def update_transcript(transcript_id: UUID, transcript: AppMmNotebookLlmChatTranscriptUpdate):
    """Update notebook LLM chat transcript by ID"""
    updated_transcript = NotebookLlmChatTranscriptService.update_transcript(transcript_id, transcript)
    if not updated_transcript:
        return ApiResponse.error({"message": "Notebook LLM chat transcript not found"})
    return ApiResponse.success(updated_transcript)

@router.delete("/delete-by-guid/{transcript_id}", response_model=ApiResponse[dict])
def delete_transcript(transcript_id: UUID):
    """Delete notebook LLM chat transcript by ID"""
    success = NotebookLlmChatTranscriptService.delete_transcript(transcript_id)
    if not success:
        return ApiResponse.error({"message": "Notebook LLM chat transcript not found"})
    return ApiResponse.success({"message": "Notebook LLM chat transcript deleted successfully"})

@router.post("/generate-test-data", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED)
def generate_test_transcripts():
    """Generate dummy chat transcript data for testing the art generator agent."""
    from uuid import UUID as _UUID
    from model.dto.reward_simulation_dto import SIMULATION_TEST_TRANSCRIPTS

    user_guid = _UUID("69cdaaa7-9800-42d9-a4c4-23db3b685a2d")
    llm_chat_hdr_guid = _UUID("70ad35aa-9216-48e6-b07c-25f85ef29383")

    try:
        created_count = 0
        for msg in SIMULATION_TEST_TRANSCRIPTS:
            transcript = AppMmNotebookLlmChatTranscriptCreate(
                user_guid=user_guid,
                llm_chat_hdr_guid=llm_chat_hdr_guid,
                msg_content=msg["msg_content"],
                sender=msg["sender"],
            )
            NotebookLlmChatTranscriptService.create_transcript(transcript)
            created_count += 1

        return ApiResponse.success({
            "message": f"Created {created_count} test chat transcripts",
            "user_guid": str(user_guid),
            "llm_chat_hdr_guid": str(llm_chat_hdr_guid),
        })
    except Exception as e:
        return ApiResponse.error({"message": str(e)})