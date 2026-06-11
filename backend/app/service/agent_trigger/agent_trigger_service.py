import os
import base64
import logging
from uuid import UUID, uuid4
from typing import Optional

from google.genai import types
from mcp.shared.exceptions import McpError

from util.supabase_config import supabase_admin

logger = logging.getLogger(__name__)


class GitlabAgentOutput:
    """Structured output from the gitlab_agent_v2 sequential pipeline."""

    def __init__(
        self,
        issue_result: Optional[str] = None,
        issue_url: Optional[str] = None,
        branch_result: Optional[str] = None,
        mr_result: Optional[str] = None,
        file_url: Optional[str] = None,
        visual_motif_result: Optional[str] = None,
    ):
        self.issue_result = issue_result
        self.issue_url = issue_url
        self.branch_result = branch_result
        self.mr_result = mr_result
        self.file_url = file_url
        self.visual_motif_result = visual_motif_result


class AgentTriggerResult:
    """Internal result from agent trigger execution."""

    def __init__(
        self,
        session_id: str,
        responses: list[str],
        storage_url: Optional[str] = None,
        visual_metaphor_prompt: Optional[str] = None,
        gitlab_output: Optional[GitlabAgentOutput] = None,
    ):
        self.session_id = session_id
        self.responses = responses
        self.storage_url = storage_url
        self.visual_metaphor_prompt = visual_metaphor_prompt
        self.gitlab_output = gitlab_output


class AgentTriggerService:

    @staticmethod
    def gitlab_agent_helper(mr_result: Optional[str]) -> Optional[str]:
        """Extract the MR ID from mr_result URL and construct the file URL.

        The mr_result is expected to be a GitLab merge request URL like:
            https://gitlab.com/paperplane-dev/PaperPlane-dev/-/merge_requests/12

        The file URL is constructed as:
            https://gitlab.com/{namespace}/{project}/-/blob/main/docs/reading-notes-{id}.md

        Returns:
            The constructed file URL, or None if extraction fails.
        """
        if not mr_result:
            return None

        # Extract the MR ID from the URL (last path segment)
        try:
            # Handle case where mr_result might have extra whitespace or newlines
            mr_url = mr_result.strip()
            # Split by '/' and grab the last segment as the ID
            segments = mr_url.rstrip("/").split("/")
            mr_id = segments[-1]

            # Validate it's numeric
            if not mr_id.isdigit():
                logger.warning(f"Could not extract numeric MR ID from: {mr_result}")
                return None

            namespace = os.environ.get("GITLAB_PROJECT_NAMESPACE", "")
            project = os.environ.get("GITLAB_PROJECT", "")

            if not namespace or not project:
                logger.warning("GITLAB_PROJECT_NAMESPACE or GITLAB_PROJECT not set in .env")
                return None

            return f"https://gitlab.com/{namespace}/{project}/-/blob/main/docs/reading-notes-{mr_id}.md"
        except Exception as e:
            logger.error(f"Error constructing file URL from mr_result '{mr_result}': {e}")
            return None

    @staticmethod
    def _parse_issue_result(issue_result_raw: Optional[str]) -> tuple[Optional[str], Optional[str]]:
        """Parse the issue_result state value into (issue_title_line, issue_url).

        The issue_creator_agent outputs two lines:
            Issue #<IID>: <title>
            URL: <issue_web_url>

        Returns:
            A tuple of (issue_title_line, issue_url). Either may be None if parsing fails.
        """
        if not issue_result_raw:
            return None, None

        lines = [line.strip() for line in issue_result_raw.strip().splitlines() if line.strip()]
        issue_title_line: Optional[str] = None
        issue_url: Optional[str] = None

        for line in lines:
            if line.startswith("Issue #"):
                issue_title_line = line
            elif line.lower().startswith("url:"):
                issue_url = line[4:].strip()

        # Fallback: if no structured URL found, use the whole string as issue_result
        if not issue_title_line:
            issue_title_line = issue_result_raw.strip()

        return issue_title_line, issue_url

    @staticmethod
    async def trigger_agent(
        user_guid: UUID,
        library_hdr_guid: UUID,
        notebook_hdr_guid: UUID,
        event_type: str,
        llm_chat_hdr_guid: Optional[UUID] = None,
        message: Optional[str] = None,
    ) -> AgentTriggerResult:
        """Execute an AI agent via Runner.run_async.

        Routes to the appropriate agent based on event_type using the text_runners registry.
        Handles session creation, multimodal injection for art evolution, image upload, and
        session state extraction.

        Args:
            user_guid: The user triggering the agent.
            library_hdr_guid: The library context.
            notebook_hdr_guid: The notebook context.
            event_type: Determines which agent runner to use.
            llm_chat_hdr_guid: Optional chat header context.
            message: Optional custom message for the agent.

        Returns:
            AgentTriggerResult with session_id, responses, storage_url, and visual_metaphor_prompt.

        Raises:
            ValueError: If event_type is not supported.
        """
        from main import text_runners, text_session_service

        # Resolve the runner for the requested event_type
        runner = text_runners.get(event_type)
        if not runner:
            supported = ", ".join(text_runners.keys())
            raise ValueError(
                f"Unsupported event_type: '{event_type}'. Supported: {supported}"
            )

        app_name = runner.app_name
        user_id = str(user_guid)
        session_id = f"trigger-{event_type}-{user_guid}-{uuid4().hex[:8]}"

        # Create a session with the required state context
        state = {
            "user_guid": str(user_guid),
            "library_hdr_guid": str(library_hdr_guid),
            "notebook_hdr_guid": str(notebook_hdr_guid),
        }
        if llm_chat_hdr_guid:
            state["llm_chat_hdr_guid"] = str(llm_chat_hdr_guid)

        await text_session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=state,
        )

        # Build the message content
        message_text = message or "Generate Legacy Art for this reading session."
        message_parts = [types.Part(text=message_text)]

        # Multimodal injection for art evolution — attach previous artwork image
        if event_type == "generate_art_evolution":
            try:
                from service.reward.app_mm_reward_line_service import AppMmRewardLineService

                # Find the reward_hdr for this library
                reward_hdr_response = supabase_admin.table("app_mm_reward_hdr").select("guid").eq(
                    "llibrary_hdr_guid", str(library_hdr_guid)
                ).order("tier_level", desc=True).limit(1).execute()

                if reward_hdr_response.data:
                    reward_hdr_guid = reward_hdr_response.data[0]["guid"]
                    latest_line = AppMmRewardLineService.get_highest_tier_by_reward_hdr(reward_hdr_guid)
                    if latest_line and latest_line.image_url:
                        logger.info(f"Injecting reference image into Gemini context: {latest_line.image_url}")
                        image_part = types.Part.from_uri(
                            file_uri=latest_line.image_url,
                            mime_type="image/png",
                        )
                        message_parts.append(image_part)
                    else:
                        logger.warning("ART_EVOLUTION triggered but no previous image URL found in reward lines.")
                else:
                    logger.warning("ART_EVOLUTION triggered but no reward_hdr found for this library.")
            except Exception as fetch_err:
                logger.error(f"Failed to pull multimodal context for evolution agent: {fetch_err}", exc_info=True)

        content = types.Content(
            parts=message_parts,
            role="user",
        )

        # Run the agent and collect responses
        responses = []
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content,
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            responses.append(part.text)
        except McpError as mcp_err:
            logger.warning(
                f"MCP tool execution failed for event_type='{event_type}': {mcp_err}"
            )
            responses.append(
                f"The external tool encountered an error: {mcp_err}. "
                "The operation may have partially succeeded — please verify."
            )

        # Retrieve session state
        session = await text_session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )
        image_base64 = session.state.get("image_base64_data") if session else None
        visual_metaphor_prompt = session.state.get("visual_metaphor_prompt") if session else None

        # Extract gitlab agent output from session state (if applicable)
        gitlab_output = None
        if session and event_type in ("gitlab_doc_v2",):
            issue_result_raw = session.state.get("issue_result")
            issue_title_line, issue_url = AgentTriggerService._parse_issue_result(issue_result_raw)
            mr_result_val = session.state.get("mr_result")
            file_url = AgentTriggerService.gitlab_agent_helper(mr_result_val)
            gitlab_output = GitlabAgentOutput(
                issue_result=issue_title_line,
                issue_url=issue_url,
                branch_result=session.state.get("branch_result"),
                mr_result=mr_result_val,
                file_url=file_url,
                visual_motif_result=session.state.get("visual_motif_result"),
            )

        # Upload image to Supabase storage if available
        storage_url = None
        if image_base64:
            try:
                storage_bucket = os.environ.get("SUPABASE_STORAGE_BUCKET")
                storage_folder = os.environ.get("SUPABASE_STORAGE_FOLDER_ART_REWARD")

                if storage_bucket and storage_folder:
                    file_bytes = base64.b64decode(image_base64)
                    filename = f"legacy_art_{uuid4().hex[:8]}.png"
                    storage_path = f"{storage_folder}/{filename}"

                    supabase_admin.storage.from_(storage_bucket).upload(
                        storage_path,
                        file_bytes,
                        {"content-type": "image/png"},
                    )

                    storage_url = supabase_admin.storage.from_(storage_bucket).get_public_url(storage_path)
            except Exception as upload_err:
                logger.error(f"Failed to upload art to storage: {upload_err}", exc_info=True)

        return AgentTriggerResult(
            session_id=session_id,
            responses=responses,
            storage_url=storage_url,
            visual_metaphor_prompt=visual_metaphor_prompt,
            gitlab_output=gitlab_output,
        )

    @staticmethod
    async def trigger_gitlab_agent(
        user_guid: UUID,
        library_hdr_guid: Optional[UUID] = None,
        focus_session_guid: Optional[UUID] = None,
    ) -> AgentTriggerResult:
        """Trigger the gitlab_sequential_agent with reading context.

        Builds a multi-part Content message (text + images) from the user's
        reading data, then passes it to the SequentialAgent pipeline
        (synthesis → issue → branch/file → merge request).

        Args:
            user_guid: The user triggering the agent.
            library_hdr_guid: Optional library context.
            focus_session_guid: Optional focus session for notes + conversation.

        Returns:
            AgentTriggerResult with session_id, responses, and gitlab_output.
        """
        from main import text_runners, text_session_service
        from service.agents.tools.agent_context_util import build_gitlab_agent_context

        # Resolve the gitlab_doc_v2 runner
        runner = text_runners.get("gitlab_doc_v2")
        if not runner:
            supported = ", ".join(text_runners.keys())
            raise ValueError(
                f"Runner 'gitlab_doc_v2' not found. Supported: {supported}"
            )

        app_name = runner.app_name
        user_id = str(user_guid)
        session_id = f"trigger-gitlab-v2-{user_guid}-{uuid4().hex[:8]}"

        # Build multi-part context (text + interleaved images)
        context_parts = build_gitlab_agent_context(
            focus_session_guid=str(focus_session_guid) if focus_session_guid else None,
            library_hdr_guid=str(library_hdr_guid) if library_hdr_guid else None,
        )

        if not context_parts:
            return AgentTriggerResult(
                session_id=session_id,
                responses=["Failed to build context: no data available."],
            )

        # Create session with state
        state = {
            "user_guid": str(user_guid),
        }
        if library_hdr_guid:
            state["library_hdr_guid"] = str(library_hdr_guid)
        if focus_session_guid:
            state["focus_session_guid"] = str(focus_session_guid)

        await text_session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=state,
        )

        # Build the multimodal Content message
        content = types.Content(
            parts=context_parts,
            role="user",
        )

        # Run the agent and collect responses
        responses = []
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content,
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            responses.append(part.text)
        except McpError as mcp_err:
            logger.warning(
                f"MCP tool execution failed for gitlab_doc_v2: {mcp_err}"
            )
            responses.append(
                f"The external tool encountered an error: {mcp_err}. "
                "The operation may have partially succeeded — please verify."
            )

        # Extract gitlab output from session state
        session = await text_session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )
        gitlab_output = None
        if session:
            issue_result_raw = session.state.get("issue_result")
            issue_title_line, issue_url = AgentTriggerService._parse_issue_result(issue_result_raw)
            mr_result_val = session.state.get("mr_result")
            file_url = AgentTriggerService.gitlab_agent_helper(mr_result_val)
            gitlab_output = GitlabAgentOutput(
                issue_result=issue_title_line,
                issue_url=issue_url,
                branch_result=session.state.get("branch_result"),
                mr_result=mr_result_val,
                file_url=file_url,
                visual_motif_result=session.state.get("visual_motif_result"),
            )

        return AgentTriggerResult(
            session_id=session_id,
            responses=responses,
            gitlab_output=gitlab_output,
        )

    @staticmethod
    async def trigger_note_taking_agent(
        notebook_hdr_guid: UUID,
        notebook_content_guid: UUID,
        image_url: str,
        highlight_metadata: dict,
    ) -> AgentTriggerResult:
        """Trigger the note_taking_agent with a highlighted image.

        Renders the highlight overlay onto the image, then passes the rendered
        image to the note_taking_agent which reads the highlighted text and
        generates a concise 15-30 word note.

        Args:
            notebook_hdr_guid: The notebook context.
            notebook_content_guid: The specific notebook content entry.
            image_url: Public URL of the source image.
            highlight_metadata: Dict with "highlights" key containing coordinate objects.

        Returns:
            AgentTriggerResult with the generated note in responses.
        """
        from main import text_runners, text_session_service
        from service.agents.tools.note_taking_tool import render_highlight_overlay

        # Resolve the note_taking runner
        runner = text_runners.get("note_taking")
        if not runner:
            supported = ", ".join(text_runners.keys())
            raise ValueError(
                f"Runner 'note_taking' not found. Supported: {supported}"
            )

        app_name = runner.app_name
        user_id = "note-taking-user"
        session_id = f"trigger-note-taking-{notebook_content_guid}-{uuid4().hex[:8]}"

        # Render the highlight overlay onto the image
        render_result = render_highlight_overlay(
            image_url=image_url,
            highlight_metadata=highlight_metadata,
        )

        if render_result.get("status") == "error":
            return AgentTriggerResult(
                session_id=session_id,
                responses=[f"Failed to render highlight: {render_result.get('message', 'Unknown error')}"],
            )

        # Read the rendered image bytes from the temp file
        temp_file_path = render_result["temp_file_path"]
        with open(temp_file_path, "rb") as f:
            image_bytes = f.read()

        # Create session
        state = {
            "notebook_hdr_guid": str(notebook_hdr_guid),
            "notebook_content_guid": str(notebook_content_guid),
        }

        await text_session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=state,
        )

        # Build multimodal message: image + text prompt
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/png",
        )
        text_part = types.Part(text="Read the highlighted text in this image and generate a concise 15-30 word note capturing the key idea.")

        content = types.Content(
            parts=[image_part, text_part],
            role="user",
        )

        # Run the agent and collect responses
        responses = []
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content,
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            responses.append(part.text)
        except Exception as e:
            logger.error(f"Note taking agent error: {e}", exc_info=True)
            responses.append(f"Agent error: {str(e)}")

        # Clean up temp file
        try:
            import os as _os
            _os.unlink(temp_file_path)
        except OSError:
            pass

        return AgentTriggerResult(
            session_id=session_id,
            responses=responses,
        )

    @staticmethod
    async def trigger_milestone_quote_agent(
        library_hdr_guid: UUID,
        reward_hdr_guid: Optional[UUID] = None,
    ) -> AgentTriggerResult:
        """Trigger the milestone_quote_agent to generate a motivational phrase.

        Builds context from the user's reading progress (book title, current tier,
        remaining hours/notes) and passes it to the milestone_quote_agent.

        Args:
            library_hdr_guid: The library (book) context.
            reward_hdr_guid: Optional reward header for milestone evaluation.

        Returns:
            AgentTriggerResult with the generated quote in responses.
        """
        from main import text_runners, text_session_service
        from service.agents.tools.agent_context_util import build_milestone_quote_agent_context

        # Resolve the milestone_quote runner
        runner = text_runners.get("milestone_quote")
        if not runner:
            supported = ", ".join(text_runners.keys())
            raise ValueError(
                f"Runner 'milestone_quote' not found. Supported: {supported}"
            )

        app_name = runner.app_name
        user_id = "milestone-quote-user"
        session_id = f"trigger-milestone-quote-{library_hdr_guid}-{uuid4().hex[:8]}"

        # Build the context string
        context_str = build_milestone_quote_agent_context(
            reward_hdr_guid=str(reward_hdr_guid) if reward_hdr_guid else None,
            library_hdr_guid=str(library_hdr_guid),
        )

        if not context_str:
            return AgentTriggerResult(
                session_id=session_id,
                responses=["No context available to generate a milestone quote."],
            )

        # Create session
        state = {
            "library_hdr_guid": str(library_hdr_guid),
        }
        if reward_hdr_guid:
            state["reward_hdr_guid"] = str(reward_hdr_guid)

        await text_session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=state,
        )

        # Build the message
        content = types.Content(
            parts=[types.Part(text=context_str)],
            role="user",
        )

        # Run the agent and collect responses
        responses = []
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content,
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            responses.append(part.text)
        except Exception as e:
            logger.error(f"Milestone quote agent error: {e}", exc_info=True)
            responses.append(f"Agent error: {str(e)}")

        return AgentTriggerResult(
            session_id=session_id,
            responses=responses,
        )

    @staticmethod
    async def trigger_art_evolution_agent(
        user_guid: UUID,
        library_hdr_guid: UUID,
        visual_motif: Optional[str] = None,
    ) -> AgentTriggerResult:
        """Trigger the art_evolution_agent with the previous artwork and a visual motif.

        Downloads the previous milestone image, then passes it along with the
        visual motif as a multimodal message to the art evolution pipeline.

        Args:
            user_guid: The user triggering the agent.
            library_hdr_guid: The library context (to look up previous reward art).
            visual_motif: Optional single-sentence visual motif string.

        Returns:
            AgentTriggerResult with session_id, responses, storage_url, and visual_metaphor_prompt.
        """
        from main import text_runners, text_session_service
        from service.agents.tools.agent_context_util import build_art_evolution_agent_context

        # Resolve the generate_art_evolution runner
        runner = text_runners.get("generate_art_evolution")
        if not runner:
            supported = ", ".join(text_runners.keys())
            raise ValueError(
                f"Runner 'generate_art_evolution' not found. Supported: {supported}"
            )

        app_name = runner.app_name
        user_id = str(user_guid)
        session_id = f"trigger-art-evolution-motif-{user_guid}-{uuid4().hex[:8]}"

        # Build context: fetch previous image and tier
        context = build_art_evolution_agent_context(
            visual_motif=visual_motif,
            library_hdr_guid=str(library_hdr_guid),
            user_guid=str(user_guid),
        )

        if context.get("status") == "error":
            return AgentTriggerResult(
                session_id=session_id,
                responses=[f"Failed to build evolution context: {context.get('message', 'Unknown error')}"],
            )

        previous_tier = context.get("previous_tier", 0)
        temp_image_file = context.get("temp_image_file")
        motif_text = visual_motif or "Evolve the artwork to reflect deeper intellectual mastery."

        # Create session with state
        state = {
            "user_guid": str(user_guid),
            "library_hdr_guid": str(library_hdr_guid),
        }

        await text_session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=state,
        )

        # Build multimodal message: previous image + text context
        message_parts = []

        # Attach the previous image
        if temp_image_file:
            try:
                with open(temp_image_file, "rb") as img_f:
                    image_bytes = img_f.read()
                message_parts.append(types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/png",
                ))
            except OSError as img_err:
                logger.warning(f"Could not read temp image {temp_image_file}: {img_err}")

        # Add the text context
        text_context = (
            f"Previous milestone image: [attached above]\n"
            f"Previous evolution: {previous_tier}\n\n"
            f"Visual motif for evolution: {motif_text}\n\n"
            f"Generate the evolutionary art based on the previous image and the new visual motif."
        )
        message_parts.append(types.Part(text=text_context))

        content = types.Content(
            parts=message_parts,
            role="user",
        )

        # Run the agent and collect responses
        responses = []
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content,
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            responses.append(part.text)
        except Exception as e:
            logger.error(f"Art evolution agent error: {e}", exc_info=True)
            responses.append(f"Agent error: {str(e)}")
        finally:
            # Clean up temp image file
            if temp_image_file:
                try:
                    import os as _os
                    _os.unlink(temp_image_file)
                except OSError:
                    pass

        # Retrieve session state
        session = await text_session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )
        image_base64 = session.state.get("image_base64_data") if session else None
        visual_metaphor_prompt = session.state.get("visual_metaphor_prompt") if session else None

        # Upload image to Supabase storage if available
        storage_url = None
        if image_base64:
            try:
                storage_bucket = os.environ.get("SUPABASE_STORAGE_BUCKET")
                storage_folder = os.environ.get("SUPABASE_STORAGE_FOLDER_ART_REWARD")

                if storage_bucket and storage_folder:
                    file_bytes = base64.b64decode(image_base64)
                    filename = f"legacy_art_{uuid4().hex[:8]}.png"
                    storage_path = f"{storage_folder}/{filename}"

                    supabase_admin.storage.from_(storage_bucket).upload(
                        storage_path,
                        file_bytes,
                        {"content-type": "image/png"},
                    )

                    storage_url = supabase_admin.storage.from_(storage_bucket).get_public_url(storage_path)
            except Exception as upload_err:
                logger.error(f"Failed to upload art to storage: {upload_err}", exc_info=True)

        return AgentTriggerResult(
            session_id=session_id,
            responses=responses,
            storage_url=storage_url,
            visual_metaphor_prompt=visual_metaphor_prompt,
        )

    @staticmethod
    async def trigger_art_agent(
        user_guid: UUID,
        visual_motif: Optional[str] = None,
    ) -> AgentTriggerResult:
        """Trigger the art_generator_agent with an optional visual motif.

        Passes the visual motif as the user message to the art pipeline.
        The SynthesisAgent uses it as the thematic foundation for generating
        the visual metaphor prompt.

        Args:
            user_guid: The user triggering the agent.
            visual_motif: Optional single-sentence visual motif string.

        Returns:
            AgentTriggerResult with session_id, responses, storage_url, and visual_metaphor_prompt.
        """
        from main import text_runners, text_session_service

        # Resolve the generate_art runner
        runner = text_runners.get("generate_art")
        if not runner:
            supported = ", ".join(text_runners.keys())
            raise ValueError(
                f"Runner 'generate_art' not found. Supported: {supported}"
            )

        app_name = runner.app_name
        user_id = str(user_guid)
        session_id = f"trigger-art-motif-{user_guid}-{uuid4().hex[:8]}"

        # Create session with state
        state = {
            "user_guid": str(user_guid),
        }

        await text_session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=state,
        )

        # Build the message — use the visual motif as the input text
        message_text = visual_motif or "Generate Legacy Art with a theme of deep intellectual focus."
        content = types.Content(
            parts=[types.Part(text=message_text)],
            role="user",
        )

        # Run the agent and collect responses
        responses = []
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content,
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            responses.append(part.text)
        except Exception as e:
            logger.error(f"Art agent error: {e}", exc_info=True)
            responses.append(f"Agent error: {str(e)}")

        # Retrieve session state
        session = await text_session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )
        image_base64 = session.state.get("image_base64_data") if session else None
        visual_metaphor_prompt = session.state.get("visual_metaphor_prompt") if session else None

        # Upload image to Supabase storage if available
        storage_url = None
        if image_base64:
            try:
                storage_bucket = os.environ.get("SUPABASE_STORAGE_BUCKET")
                storage_folder = os.environ.get("SUPABASE_STORAGE_FOLDER_ART_REWARD")

                if storage_bucket and storage_folder:
                    file_bytes = base64.b64decode(image_base64)
                    filename = f"legacy_art_{uuid4().hex[:8]}.png"
                    storage_path = f"{storage_folder}/{filename}"

                    supabase_admin.storage.from_(storage_bucket).upload(
                        storage_path,
                        file_bytes,
                        {"content-type": "image/png"},
                    )

                    storage_url = supabase_admin.storage.from_(storage_bucket).get_public_url(storage_path)
            except Exception as upload_err:
                logger.error(f"Failed to upload art to storage: {upload_err}", exc_info=True)

        return AgentTriggerResult(
            session_id=session_id,
            responses=responses,
            storage_url=storage_url,
            visual_metaphor_prompt=visual_metaphor_prompt,
        )


