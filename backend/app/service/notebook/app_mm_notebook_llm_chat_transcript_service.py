from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime
from util.supabase_config import supabase
from model.notebook.app_mm_notebook_llm_chat_transcript import (
    AppMmNotebookLlmChatTranscriptCreate,
    AppMmNotebookLlmChatTranscriptUpdate,
    AppMmNotebookLlmChatTranscriptResponse
)

class NotebookLlmChatTranscriptService:
    TABLE_NAME = "app_mm_notebook_llm_chat_transcript"
    
    @staticmethod
    def create_transcript(transcript_data: AppMmNotebookLlmChatTranscriptCreate) -> AppMmNotebookLlmChatTranscriptResponse:
        """Create a new notebook LLM chat transcript"""
        new_transcript = {
            "guid": str(uuid4()),
            "user_guid": str(transcript_data.user_guid),
            "llm_chat_hdr_guid": str(transcript_data.llm_chat_hdr_guid),
            "msg_content": transcript_data.msg_content,
            "sender": transcript_data.sender,
            "focus_session_guid": str(transcript_data.focus_session_guid) if transcript_data.focus_session_guid else None
        }
        
        response = supabase.table(NotebookLlmChatTranscriptService.TABLE_NAME).insert(new_transcript).execute()
        
        if not response.data:
            raise Exception("Failed to create notebook LLM chat transcript")
        
        return AppMmNotebookLlmChatTranscriptResponse(**response.data[0])
    
    @staticmethod
    def get_transcript_by_id(transcript_id: UUID) -> Optional[AppMmNotebookLlmChatTranscriptResponse]:
        """Get notebook LLM chat transcript by GUID"""
        response = supabase.table(NotebookLlmChatTranscriptService.TABLE_NAME).select("*").eq("guid", str(transcript_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmNotebookLlmChatTranscriptResponse(**response.data[0])
    
    @staticmethod
    def get_all_transcripts() -> List[AppMmNotebookLlmChatTranscriptResponse]:
        """Get all notebook LLM chat transcripts"""
        response = supabase.table(NotebookLlmChatTranscriptService.TABLE_NAME).select("*").execute()
        
        return [AppMmNotebookLlmChatTranscriptResponse(**transcript) for transcript in response.data]
    
    @staticmethod
    def get_transcripts_by_user(user_guid: UUID) -> List[AppMmNotebookLlmChatTranscriptResponse]:
        """Get all notebook LLM chat transcripts for a specific user"""
        response = supabase.table(NotebookLlmChatTranscriptService.TABLE_NAME).select("*").eq("user_guid", str(user_guid)).execute()
        
        return [AppMmNotebookLlmChatTranscriptResponse(**transcript) for transcript in response.data]
    
    @staticmethod
    def get_transcripts_by_chat_hdr(llm_chat_hdr_guid: UUID) -> List[AppMmNotebookLlmChatTranscriptResponse]:
        """Get all notebook LLM chat transcripts for a specific chat header"""
        response = supabase.table(NotebookLlmChatTranscriptService.TABLE_NAME).select("*").eq("llm_chat_hdr_guid", str(llm_chat_hdr_guid)).order("created_date").execute()
        
        return [AppMmNotebookLlmChatTranscriptResponse(**transcript) for transcript in response.data]
    
    @staticmethod
    def count_transcripts_by_chat_hdr(llm_chat_hdr_guid: UUID) -> int:
        """Count total transcripts for a specific chat header"""
        response = (
            supabase.table(NotebookLlmChatTranscriptService.TABLE_NAME)
            .select("guid", count="exact")
            .eq("llm_chat_hdr_guid", str(llm_chat_hdr_guid))
            .execute()
        )
        return response.count if response.count is not None else 0

    @staticmethod
    def get_transcripts_by_notebook(notebook_hdr_guid: UUID, llm_chat_hdr_guid: UUID) -> List[AppMmNotebookLlmChatTranscriptResponse]:
        """Get all notebook LLM chat transcripts for a specific notebook via chat header"""
        response = supabase.table(NotebookLlmChatTranscriptService.TABLE_NAME).select("*").eq("llm_chat_hdr_guid", str(llm_chat_hdr_guid)).order("created_date").execute()
        
        return [AppMmNotebookLlmChatTranscriptResponse(**transcript) for transcript in response.data]
    
    @staticmethod
    def update_transcript(transcript_id: UUID, transcript_data: AppMmNotebookLlmChatTranscriptUpdate) -> Optional[AppMmNotebookLlmChatTranscriptResponse]:
        """Update notebook LLM chat transcript by GUID"""
        update_data = transcript_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return NotebookLlmChatTranscriptService.get_transcript_by_id(transcript_id)
        
        # Convert UUIDs to strings
        if "user_guid" in update_data:
            update_data["user_guid"] = str(update_data["user_guid"])
        if "llm_chat_hdr_guid" in update_data:
            update_data["llm_chat_hdr_guid"] = str(update_data["llm_chat_hdr_guid"])
        if "focus_session_guid" in update_data:
            update_data["focus_session_guid"] = str(update_data["focus_session_guid"]) if update_data["focus_session_guid"] else None
        
        # Add updated_date
        update_data["updated_date"] = datetime.now().isoformat()
        
        response = supabase.table(NotebookLlmChatTranscriptService.TABLE_NAME).update(update_data).eq("guid", str(transcript_id)).execute()
        
        if not response.data:
            return None
        
        return AppMmNotebookLlmChatTranscriptResponse(**response.data[0])
    
    @staticmethod
    def delete_transcript(transcript_id: UUID) -> bool:
        """Delete notebook LLM chat transcript by GUID"""
        response = supabase.table(NotebookLlmChatTranscriptService.TABLE_NAME).delete().eq("guid", str(transcript_id)).execute()
        
        return len(response.data) > 0


    @staticmethod
    def get_chat_transcripts_by_focus_session(focus_session_guid: UUID, turns: int = 3) -> str:
        """Get the last N conversation turns (user + assistant pairs) for a focus session.

        Queries transcripts by focus_session_guid ordered by created_date descending,
        then extracts the most recent N user messages and their corresponding assistant
        messages, returning them as a formatted string.

        Args:
            focus_session_guid: The UUID of the focus session.
            turns: Number of conversation turns to retrieve. Defaults to 3.

        Returns:
            A string with up to N user/assistant pairs formatted as:
            "user: ...\\nassistant: ...\\n" repeated for each turn.
            Returns empty string if no transcripts found.
        """
        # Fetch recent transcripts ordered by created_date descending
        # Fetch extra records to account for potential gaps
        fetch_limit = max(turns * 4, 20)
        response = (
            supabase.table(NotebookLlmChatTranscriptService.TABLE_NAME)
            .select("msg_content, sender, created_date")
            .eq("focus_session_guid", str(focus_session_guid))
            .order("created_date", desc=True)
            .limit(fetch_limit)
            .execute()
        )

        if not response.data:
            return ""

        # Reverse to chronological order for pairing
        records = list(reversed(response.data))

        # Pair user messages with their following assistant messages
        paired_turns: list[tuple[str, str]] = []
        i = 0
        while i < len(records):
            if records[i]["sender"] == "user":
                user_msg = records[i]["msg_content"]
                assistant_msg = ""
                # Look for the next assistant message
                if i + 1 < len(records) and records[i + 1]["sender"] == "assistant":
                    assistant_msg = records[i + 1]["msg_content"]
                    i += 2
                else:
                    i += 1
                paired_turns.append((user_msg, assistant_msg))
            else:
                i += 1

        # Take the last N turns
        last_turns = paired_turns[-turns:] if len(paired_turns) >= turns else paired_turns

        # Format as string
        output_lines = []
        for user_msg, assistant_msg in last_turns:
            output_lines.append(f"user: {user_msg}")
            output_lines.append(f"assistant: {assistant_msg}")

        return "\n".join(output_lines)