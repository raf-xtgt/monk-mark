from uuid import UUID, uuid4
from typing import List, Optional, Literal
from enum import Enum
from util.supabase_config import supabase
from model.reward.app_mm_reward_hdr import AppMmRewardHdrCreate, AppMmRewardHdrUpdate, AppMmRewardHdrResponse
from model.dto.reward_output_dto import RewardOutputDto, MilestoneEvaluation


class MilestoneRemarks(str, Enum):
    MAX_TIER_REACHED = "Congratulations! You've reached the highest tier for this book. Consider picking up a new book to continue your growth journey."
    TIER_UNLOCKED = "Amazing work! You've unlocked a new tier. Your Legacy Art reward is being generated."
    KEEP_GOING = "You're making progress. Keep focusing and taking notes to unlock your next Legacy Art reward."


class AppMmRewardHdrService:
    TABLE_NAME = "app_mm_reward_hdr"
    FOCUS_SESSION_TABLE = "app_mm_focus_session"
    NOTEBOOK_CONTENT_TABLE = "app_mm_notebook_content"

    @staticmethod
    def create_reward_hdr(reward_data: AppMmRewardHdrCreate) -> AppMmRewardHdrResponse:
        """Create a new reward header"""
        new_reward = {
            "guid": str(uuid4()),
            "user_guid": str(reward_data.user_guid),
            "llibrary_hdr_guid": str(reward_data.library_hdr_guid),
            "notebook_hdr_guid": str(reward_data.notebook_hdr_guid),
            "image_url": reward_data.image_url,
            "file_upload_guid": str(reward_data.file_upload_guid) if reward_data.file_upload_guid else None,
            "tier_level": reward_data.tier_level,
            "trigger_session_guid": str(reward_data.trigger_session_guid) if reward_data.trigger_session_guid else None,
            "reward_metadata": reward_data.reward_metadata,
        }

        response = supabase.table(AppMmRewardHdrService.TABLE_NAME).insert(new_reward).execute()

        if not response.data:
            raise Exception("Failed to create reward header")

        row = response.data[0]
        # Map the DB column name (llibrary_hdr_guid) to the model field (library_hdr_guid)
        row["library_hdr_guid"] = row.pop("llibrary_hdr_guid", None)
        return AppMmRewardHdrResponse(**row)

    @staticmethod
    def get_reward_hdr_by_id(reward_id: UUID) -> Optional[AppMmRewardHdrResponse]:
        """Get reward header by GUID"""
        response = supabase.table(AppMmRewardHdrService.TABLE_NAME).select("*").eq("guid", str(reward_id)).execute()

        if not response.data:
            return None

        row = response.data[0]
        row["library_hdr_guid"] = row.pop("llibrary_hdr_guid", None)
        return AppMmRewardHdrResponse(**row)

    @staticmethod
    def get_all_reward_hdrs() -> List[AppMmRewardHdrResponse]:
        """Get all reward headers"""
        response = supabase.table(AppMmRewardHdrService.TABLE_NAME).select("*").execute()

        results = []
        for row in response.data:
            row["library_hdr_guid"] = row.pop("llibrary_hdr_guid", None)
            results.append(AppMmRewardHdrResponse(**row))
        return results

    @staticmethod
    def get_reward_hdrs_by_user(user_guid: UUID) -> List[AppMmRewardHdrResponse]:
        """Get all reward headers for a specific user"""
        response = supabase.table(AppMmRewardHdrService.TABLE_NAME).select("*").eq("user_guid", str(user_guid)).execute()

        results = []
        for row in response.data:
            row["library_hdr_guid"] = row.pop("llibrary_hdr_guid", None)
            results.append(AppMmRewardHdrResponse(**row))
        return results

    @staticmethod
    def get_reward_hdrs_by_notebook(notebook_hdr_guid: UUID) -> List[AppMmRewardHdrResponse]:
        """Get all reward headers for a specific notebook"""
        response = supabase.table(AppMmRewardHdrService.TABLE_NAME).select("*").eq("notebook_hdr_guid", str(notebook_hdr_guid)).execute()

        results = []
        for row in response.data:
            row["library_hdr_guid"] = row.pop("llibrary_hdr_guid", None)
            results.append(AppMmRewardHdrResponse(**row))
        return results

    @staticmethod
    def update_reward_hdr(reward_id: UUID, reward_data: AppMmRewardHdrUpdate) -> Optional[AppMmRewardHdrResponse]:
        """Update reward header by GUID"""
        update_data = reward_data.model_dump(exclude_unset=True)

        if not update_data:
            return AppMmRewardHdrService.get_reward_hdr_by_id(reward_id)

        # Map model field name to DB column name for the update payload
        if "library_hdr_guid" in update_data:
            update_data["llibrary_hdr_guid"] = str(update_data.pop("library_hdr_guid"))

        # Convert UUIDs to strings for Supabase
        for key in ["user_guid", "notebook_hdr_guid", "file_upload_guid", "trigger_session_guid"]:
            if key in update_data and update_data[key] is not None:
                update_data[key] = str(update_data[key])

        response = supabase.table(AppMmRewardHdrService.TABLE_NAME).update(update_data).eq("guid", str(reward_id)).execute()

        if not response.data:
            return None

        row = response.data[0]
        row["library_hdr_guid"] = row.pop("llibrary_hdr_guid", None)
        return AppMmRewardHdrResponse(**row)

    @staticmethod
    def delete_reward_hdr(reward_id: UUID) -> bool:
        """Delete reward header by GUID"""
        response = supabase.table(AppMmRewardHdrService.TABLE_NAME).delete().eq("guid", str(reward_id)).execute()

        return len(response.data) > 0

    @staticmethod
    def get_reward_summary_by_library(user_guid: UUID, library_hdr_guid: UUID) -> RewardOutputDto:
        """Get reward summary for a library: rewards list, total focused hours, and total notes"""

        # 1. Retrieve reward headers by library_hdr_guid
        reward_response = supabase.table(AppMmRewardHdrService.TABLE_NAME).select("*").eq(
            "llibrary_hdr_guid", str(library_hdr_guid)
        ).execute()

        reward_list: List[AppMmRewardHdrResponse] = []
        for row in reward_response.data:
            row["library_hdr_guid"] = row.pop("llibrary_hdr_guid", None)
            reward_list.append(AppMmRewardHdrResponse(**row))

        # 2. Retrieve focus session stats by library_hdr_guid
        focus_response = supabase.table(AppMmRewardHdrService.FOCUS_SESSION_TABLE).select(
            "time_hrs, time_seconds"
        ).eq("library_hdr_guid", str(library_hdr_guid)).execute()

        total_hrs = 0.0
        total_seconds = 0
        for session in focus_response.data:
            if session.get("time_hrs"):
                try:
                    total_hrs += float(session["time_hrs"])
                except (ValueError, TypeError):
                    pass
            if session.get("time_seconds"):
                total_seconds += int(session["time_seconds"])

        total_focused_hrs = total_hrs + (total_seconds / 3600.0)

        # 3. Retrieve total notebook content count by library_hdr_guid
        content_response = supabase.table(AppMmRewardHdrService.NOTEBOOK_CONTENT_TABLE).select(
            "guid", count="exact"
        ).eq("library_hdr_guid", str(library_hdr_guid)).execute()

        total_notes = content_response.count if content_response.count is not None else 0

        return RewardOutputDto(
            user_guid=user_guid,
            library_hdr_guid=library_hdr_guid,
            reward_list=reward_list,
            total_focused_hrs=round(total_focused_hrs, 2),
            total_notes=total_notes,
            milestone_evaluation=AppMmRewardHdrService.evaluate_milestone_progression(
                tier_level=len(reward_list),
                total_focus_hours=round(total_focused_hrs, 2),
                total_notes_taken=total_notes,
            ),
        )

    @staticmethod
    def evaluate_milestone_progression(
        tier_level: int,
        total_focus_hours: float,
        total_notes_taken: int,
    ) -> MilestoneEvaluation:
        """Evaluate milestone progression using geometric progression thresholds.

        Formulas:
            Hour Threshold: H(n) = 6 * (2^n - 1)
            Note Threshold: N(n) = 3 * n^2

        Args:
            tier_level: Current milestone level achieved (starts at 0).
            total_focus_hours: Cumulative focus hours logged for this book.
            total_notes_taken: Cumulative notes linked to this book.

        Returns:
            MilestoneEvaluation with thresholds, progress, and agent routing.
        """
        next_tier = tier_level + 1

        # 1. Threshold Calculations
        h_prev = 6 * (2 ** tier_level - 1) if tier_level > 0 else 0.0
        h_target = 6 * (2 ** next_tier - 1)
        n_target = 3 * (next_tier ** 2)

        # 2. Hour Completion Percentage (within current tier bracket)
        if h_target == h_prev:
            hour_pct = 0.0
        else:
            hour_pct = ((total_focus_hours - h_prev) / (h_target - h_prev)) * 100
        hour_pct = max(0.0, min(100.0, hour_pct))

        # 3. Note Completion Ratio
        display_notes = min(total_notes_taken, n_target)
        note_ratio = f"{display_notes}/{n_target}"

        # Note Completion Percentage
        if n_target == 0:
            note_pct = 0.0
        else:
            note_pct = (total_notes_taken / n_target) * 100
        note_pct = max(0.0, min(100.0, note_pct))

        # 4. Fulfilled Flags
        is_hour_fulfilled = total_focus_hours >= h_target
        is_note_fulfilled = total_notes_taken >= n_target

        # 5. Agent Routing
        remarks: Optional[str] = None
        remaining_hours: Optional[float] = None
        remaining_notes: Optional[int] = None
        MAX_TIER = 5

        if tier_level >= MAX_TIER:
            # Already at max tier — no further progression
            agent_action: Literal["ART_GEN", "ART_EVOLUTION", "NO_AGENT"] = "NO_AGENT"
            remarks = MilestoneRemarks.MAX_TIER_REACHED.value
        elif is_hour_fulfilled and is_note_fulfilled:
            agent_action = "ART_GEN" if tier_level == 0 else "ART_EVOLUTION"
            # Increment tier_level since milestone is fulfilled
            tier_level += 1
            next_tier = tier_level + 1
            # Cap at max tier after increment
            if tier_level >= MAX_TIER:
                tier_level = MAX_TIER
                next_tier = MAX_TIER
            remarks = MilestoneRemarks.TIER_UNLOCKED.value
        else:
            agent_action = "NO_AGENT"
            # Calculate remaining hours and notes needed
            remaining_hours = round(max(0.0, h_target - total_focus_hours), 2)
            remaining_notes = max(0, n_target - total_notes_taken)
            remarks = (
                f"{MilestoneRemarks.KEEP_GOING.value} "
                f"You need {remaining_hours} more hours and {remaining_notes} more notes to reach Evolution {next_tier}."
            )

        return MilestoneEvaluation(
            current_tier=tier_level,
            next_tier=next_tier,
            hour_threshold=float(h_target),
            note_threshold=int(n_target),
            hour_completion_percentage=round(hour_pct, 2),
            note_completion_percentage=round(note_pct, 2),
            note_completion_ratio=note_ratio,
            is_hour_fulfilled=is_hour_fulfilled,
            is_note_fulfilled=is_note_fulfilled,
            agent_to_trigger=agent_action,
            remarks=remarks,
            remaining_hours=remaining_hours,
            remaining_notes=remaining_notes,
        )

    @staticmethod
    def generate_test_data(tier_level: int, progress_type: str) -> dict:
        """Generate test data for monk mode milestone testing.

        Creates focus sessions and notebook contents to simulate a user at a specific
        progression point toward the next tier.

        Args:
            tier_level: The current tier the user has already achieved.
            progress_type: 'HALF' for 50% progress toward next tier, 'FULL' for 100%.

        Returns:
            Summary of created test data.
        """
        from model.focus_session.app_mm_focus_session import AppMmFocusSessionCreate
        from model.notebook.app_mm_notebook_content import AppMmNotebookContentCreate
        from service.focus_session.app_mm_focus_session_service import AppMmFocusSessionService
        from service.notebook.app_mm_notebook_content_service import AppMmNotebookContentService
        from decimal import Decimal

        user_guid = UUID("69cdaaa7-9800-42d9-a4c4-23db3b685a2d")
        notebook_hdr_guid = UUID("f28ede59-922b-4261-9e74-da6ff0d6e480")
        library_hdr_guid = UUID("dede4054-06bb-41b6-bc03-ac74b241160e")

        next_tier = tier_level + 1

        # Calculate thresholds for the next tier
        h_target = 6 * (2 ** next_tier - 1)
        n_target = 3 * (next_tier ** 2)

        # Calculate what already exists (from previous tiers)
        h_prev = 6 * (2 ** tier_level - 1) if tier_level > 0 else 0.0

        # Determine target hours and notes based on progress_type
        if progress_type == "HALF":
            # Halfway between previous tier threshold and next tier threshold
            target_hours = h_prev + (h_target - h_prev) * 0.5
            target_notes = int(n_target * 0.5)
        else:  # FULL
            target_hours = float(h_target)
            target_notes = n_target

        # Query existing focus sessions to see what's already there
        existing_focus = supabase.table(AppMmRewardHdrService.FOCUS_SESSION_TABLE).select(
            "time_hrs, time_seconds"
        ).eq("library_hdr_guid", str(library_hdr_guid)).execute()

        existing_hrs = 0.0
        for session in existing_focus.data:
            if session.get("time_hrs"):
                try:
                    existing_hrs += float(session["time_hrs"])
                except (ValueError, TypeError):
                    pass
            if session.get("time_seconds"):
                existing_hrs += int(session["time_seconds"]) / 3600.0

        # Query existing notebook contents
        existing_notes_resp = supabase.table(AppMmRewardHdrService.NOTEBOOK_CONTENT_TABLE).select(
            "guid", count="exact"
        ).eq("library_hdr_guid", str(library_hdr_guid)).execute()
        existing_notes = existing_notes_resp.count if existing_notes_resp.count is not None else 0

        # Calculate how much more to create
        hours_to_add = max(0.0, target_hours - existing_hrs)
        notes_to_add = max(0, target_notes - existing_notes)

        # Create focus sessions (split into 1-hour chunks for realism)
        sessions_created = 0
        remaining_hours = hours_to_add
        while remaining_hours > 0:
            chunk_hrs = min(remaining_hours, 1.0)
            session_data = AppMmFocusSessionCreate(
                user_guid=user_guid,
                library_hdr_guid=library_hdr_guid,
                time_hrs=Decimal(str(round(chunk_hrs, 4))),
                time_seconds=0,
            )
            AppMmFocusSessionService.create_focus_session(session_data)
            sessions_created += 1
            remaining_hours -= chunk_hrs

        # Create notebook contents
        notes_created = 0
        for i in range(notes_to_add):
            seq = existing_notes + i + 1
            content_data = AppMmNotebookContentCreate(
                user_guid=user_guid,
                notebook_hdr_guid=notebook_hdr_guid,
                library_hdr_guid=library_hdr_guid,
                content_text=f"Test note #{seq} for tier {tier_level} → {next_tier} ({progress_type} progression).",
                sequence_no=seq,
            )
            AppMmNotebookContentService.create_notebook_content(content_data)
            notes_created += 1

        return {
            "tier_level": tier_level,
            "progress_type": progress_type,
            "target_hours": round(target_hours, 2),
            "target_notes": target_notes,
            "hours_added": round(hours_to_add, 2),
            "notes_added": notes_to_add,
            "focus_sessions_created": sessions_created,
            "notebook_contents_created": notes_created,
            "user_guid": str(user_guid),
            "library_hdr_guid": str(library_hdr_guid),
            "notebook_hdr_guid": str(notebook_hdr_guid),
        }

    @staticmethod
    def simulate_reward_flow(
        user_guid: UUID,
        library_hdr_guid: UUID,
        tier_level: int,
        progress_type: str,
    ) -> dict:
        """Simulate the full reward flow: create notebook/notes/focus sessions, evaluate, and trigger agent.

        Args:
            user_guid: The user to simulate for.
            library_hdr_guid: The library to simulate against.
            tier_level: The current tier already achieved.
            progress_type: 'HALF' for 50% progress, 'FULL' for 100% (triggers art gen).

        Returns:
            Summary dict with all created data and evaluation results.
        """
        from model.focus_session.app_mm_focus_session import AppMmFocusSessionCreate
        from model.notebook.app_mm_notebook_content import AppMmNotebookContentCreate
        from model.notebook.app_mm_notebook_hdr import AppMmNotebookHdrCreate
        from service.focus_session.app_mm_focus_session_service import AppMmFocusSessionService
        from service.notebook.app_mm_notebook_content_service import AppMmNotebookContentService
        from service.notebook.app_mm_notebook_hdr_service import AppMmNotebookHdrService
        from decimal import Decimal

        next_tier = tier_level + 1

        # Calculate thresholds
        h_target = 6 * (2 ** next_tier - 1)
        n_target = 3 * (next_tier ** 2)
        h_prev = 6 * (2 ** tier_level - 1) if tier_level > 0 else 0.0

        # Determine targets based on progress_type
        if progress_type == "HALF":
            target_hours = h_prev + (h_target - h_prev) * 0.5
            target_notes = int(n_target * 0.5)
        else:  # FULL
            target_hours = float(h_target)
            target_notes = n_target

        # --- Step 1: Create focus sessions first (so we have focus_session_guid for downstream records) ---
        existing_focus = supabase.table(AppMmRewardHdrService.FOCUS_SESSION_TABLE).select(
            "time_hrs, time_seconds"
        ).eq("library_hdr_guid", str(library_hdr_guid)).execute()

        existing_hrs = 0.0
        for session in existing_focus.data:
            if session.get("time_hrs"):
                try:
                    existing_hrs += float(session["time_hrs"])
                except (ValueError, TypeError):
                    pass
            if session.get("time_seconds"):
                existing_hrs += int(session["time_seconds"]) / 3600.0

        hours_to_add = max(0.0, target_hours - existing_hrs)
        sessions_created = 0
        last_focus_session_guid = None
        remaining_hours = hours_to_add
        while remaining_hours > 0:
            chunk_hrs = min(remaining_hours, 1.0)
            session_data = AppMmFocusSessionCreate(
                user_guid=user_guid,
                library_hdr_guid=library_hdr_guid,
                time_hrs=Decimal(str(round(chunk_hrs, 4))),
                time_seconds=0,
            )
            created_session = AppMmFocusSessionService.create_focus_session(session_data)
            last_focus_session_guid = created_session.guid
            sessions_created += 1
            remaining_hours -= chunk_hrs

        # --- Step 2: Ensure notebook_hdr exists ---
        notebook_hdr_response = supabase.table("app_mm_notebook_hdr").select("*").eq(
            "library_hdr_guid", str(library_hdr_guid)
        ).order("updated_date", desc=True).limit(1).execute()

        if notebook_hdr_response.data:
            notebook_hdr_guid = notebook_hdr_response.data[0]["guid"]
            notebook_created = False
        else:
            # Create a dummy notebook_hdr
            new_notebook = AppMmNotebookHdrCreate(
                user_guid=user_guid,
                library_hdr_guid=library_hdr_guid,
                running_no="SIM-001",
                name="Simulation Notebook",
            )
            created_notebook = AppMmNotebookHdrService.create_notebook_hdr(new_notebook)
            notebook_hdr_guid = created_notebook.guid
            notebook_created = True

        # --- Step 3: Create notebook contents as needed (with focus_session_guid) ---
        existing_notes_resp = supabase.table(AppMmRewardHdrService.NOTEBOOK_CONTENT_TABLE).select(
            "guid", count="exact"
        ).eq("library_hdr_guid", str(library_hdr_guid)).execute()
        existing_notes = existing_notes_resp.count if existing_notes_resp.count is not None else 0

        notes_to_add = max(0, target_notes - existing_notes)
        notes_created = 0
        for i in range(notes_to_add):
            seq = existing_notes + i + 1
            # Use simulation test notes if available, otherwise generate generic text
            from model.dto.reward_simulation_dto import SIMULATION_TEST_NOTES
            note_index = i % len(SIMULATION_TEST_NOTES)
            note_text = SIMULATION_TEST_NOTES[note_index]["content_text"]
            content_data = AppMmNotebookContentCreate(
                user_guid=user_guid,
                notebook_hdr_guid=notebook_hdr_guid,
                library_hdr_guid=library_hdr_guid,
                focus_session_guid=last_focus_session_guid,
                content_text=note_text,
                sequence_no=seq,
            )
            AppMmNotebookContentService.create_notebook_content(content_data)
            notes_created += 1

        # --- Step 4: Ensure llm_chat_hdr and transcripts exist (with focus_session_guid) ---
        from model.notebook.app_mm_notebook_llm_chat_hdr import AppMmNotebookLlmChatHdrCreate
        from model.notebook.app_mm_notebook_llm_chat_transcript import AppMmNotebookLlmChatTranscriptCreate
        from service.notebook.app_mm_notebook_llm_chat_hdr_service import NotebookLlmChatHdrService
        from service.notebook.app_mm_notebook_llm_chat_transcript_service import NotebookLlmChatTranscriptService

        # Check for existing chat_hdr under this notebook_hdr
        chat_hdr_response = supabase.table("app_mm_notebook_llm_chat_hdr").select("*").eq(
            "notebook_hdr_guid", str(notebook_hdr_guid)
        ).order("updated_date", desc=True).limit(1).execute()

        llm_chat_hdr_guid = None
        chat_hdr_created = False
        if chat_hdr_response.data:
            llm_chat_hdr_guid = chat_hdr_response.data[0]["guid"]
        else:
            # Create a new chat_hdr
            new_chat_hdr = AppMmNotebookLlmChatHdrCreate(
                user_guid=user_guid,
                notebook_hdr_guid=notebook_hdr_guid,
                library_hdr_guid=library_hdr_guid,
            )
            created_chat_hdr = NotebookLlmChatHdrService.create_chat_hdr(new_chat_hdr)
            llm_chat_hdr_guid = created_chat_hdr.guid
            chat_hdr_created = True

        # Check for existing transcripts under this chat_hdr
        transcripts_created = 0
        existing_transcripts_resp = supabase.table("app_mm_notebook_llm_chat_transcript").select(
            "guid", count="exact"
        ).eq("llm_chat_hdr_guid", str(llm_chat_hdr_guid)).execute()
        existing_transcripts = existing_transcripts_resp.count if existing_transcripts_resp.count is not None else 0

        if existing_transcripts == 0:
            # Create simulation transcripts from centralized test data
            from model.dto.reward_simulation_dto import SIMULATION_TEST_TRANSCRIPTS
            for transcript in SIMULATION_TEST_TRANSCRIPTS:
                transcript_data = AppMmNotebookLlmChatTranscriptCreate(
                    user_guid=user_guid,
                    llm_chat_hdr_guid=llm_chat_hdr_guid,
                    msg_content=transcript["msg_content"],
                    sender=transcript["sender"],
                    focus_session_guid=last_focus_session_guid,
                )
                NotebookLlmChatTranscriptService.create_transcript(transcript_data)
                transcripts_created += 1

        # --- Step 5: Evaluate milestone ---
        summary = AppMmRewardHdrService.get_reward_summary_by_library(user_guid, library_hdr_guid)
        evaluation = AppMmRewardHdrService.evaluate_milestone_progression(
            tier_level=len(summary.reward_list),
            total_focus_hours=summary.total_focused_hrs,
            total_notes_taken=summary.total_notes,
        )

        return {
            "user_guid": str(user_guid),
            "library_hdr_guid": str(library_hdr_guid),
            "notebook_hdr_guid": str(notebook_hdr_guid),
            "llm_chat_hdr_guid": str(llm_chat_hdr_guid),
            "focus_session_guid": str(last_focus_session_guid) if last_focus_session_guid else None,
            "notebook_created": notebook_created,
            "chat_hdr_created": chat_hdr_created,
            "notes_created": notes_created,
            "transcripts_created": transcripts_created,
            "sessions_created": sessions_created,
            "target_hours": round(target_hours, 2),
            "target_notes": target_notes,
            "evaluation": evaluation.model_dump(),
        }

# TODO: helper method for the simulation endpoint