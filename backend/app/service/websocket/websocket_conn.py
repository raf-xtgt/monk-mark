"""
WebSocket Handler for Nova Sonic Voice Tutor

Manages WebSocket connections for real-time bidirectional audio streaming
between React Native frontend and AWS Bedrock Nova Sonic model.
"""

import asyncio
import json
import logging
import base64
from datetime import datetime
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

from service.notebook.app_mm_notebook_llm_chat_transcript_service import (
    NotebookLlmChatTranscriptService,
)
from model.notebook.app_mm_notebook_llm_chat_transcript import (
    AppMmNotebookLlmChatTranscriptCreate,
)
from service.agents.tools.agent_context_util import build_socratic_agent_context

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _fallback_save_turn(
    user_guid: str | None,
    llm_chat_hdr_guid: str | None,
    user_message: str,
    assistant_message: str,
    focus_session_guid: str | None = None,
) -> None:
    """Fallback persistence for a conversation turn.

    Called when the ADK agent does not invoke save_conversation_turn itself
    (e.g., on subsequent turns where the LLM forgets the instruction).
    This ensures every turn is persisted regardless of agent behavior.
    """
    if not user_guid or not llm_chat_hdr_guid:
        logger.warning(
            "Fallback save skipped: missing identifiers "
            f"(user_guid={user_guid}, llm_chat_hdr_guid={llm_chat_hdr_guid})"
        )
        return

    try:
        if user_message and user_message.strip():
            user_transcript = AppMmNotebookLlmChatTranscriptCreate(
                user_guid=UUID(user_guid),
                llm_chat_hdr_guid=UUID(llm_chat_hdr_guid),
                msg_content=user_message.strip(),
                sender="user",
                focus_session_guid=UUID(focus_session_guid) if focus_session_guid else None,
            )
            NotebookLlmChatTranscriptService.create_transcript(user_transcript)
            logger.info(
                f"[Fallback] Saved user message for chat {llm_chat_hdr_guid}: "
                f"{user_message[:80]}..."
            )

        if assistant_message and assistant_message.strip():
            assistant_transcript = AppMmNotebookLlmChatTranscriptCreate(
                user_guid=UUID(user_guid),
                llm_chat_hdr_guid=UUID(llm_chat_hdr_guid),
                msg_content=assistant_message.strip(),
                sender="assistant",
                focus_session_guid=UUID(focus_session_guid) if focus_session_guid else None,
            )
            NotebookLlmChatTranscriptService.create_transcript(assistant_transcript)
            logger.info(
                f"[Fallback] Saved assistant message for chat {llm_chat_hdr_guid}: "
                f"{assistant_message[:80]}..."
            )
    except Exception as e:
        logger.error(f"[Fallback] save_turn error: {e}", exc_info=True)


async def voice_tutor_endpoint(websocket: WebSocket, appName, agent, runner, session_service):
    """WebSocket endpoint for bidirectional streaming with ADK.

    Accepts context parameters via query params or an initial JSON message of type 'context'.
    These are injected into ADK Session State so all agents can access them.

    Query params (all optional):
        user_guid, library_hdr_guid, notebook_hdr_guid, llm_chat_hdr_guid, focus_session_guid

    Args:
        websocket: The WebSocket connection
        appName: ADK application name
        agent: The root voice agent (socratic_dialogue_agent)
        runner: The ADK Runner instance
        session_service: The ADK InMemorySessionService instance
    """
    # Extract context identifiers from query params
    query_params = dict(websocket.query_params)
    user_guid = query_params.get("user_guid")
    library_hdr_guid = query_params.get("library_hdr_guid")
    notebook_hdr_guid = query_params.get("notebook_hdr_guid")
    llm_chat_hdr_guid = query_params.get("llm_chat_hdr_guid")
    focus_session_guid = query_params.get("focus_session_guid")

    user_id = user_guid or "test-user"
    session_id = query_params.get("session_id", "test-session")
    logger.debug(
        f"WebSocket connection request: user_id={user_id}, session_id={session_id}, "
        f"user_guid={user_guid}, library_hdr_guid={library_hdr_guid}, "
        f"notebook_hdr_guid={notebook_hdr_guid}, llm_chat_hdr_guid={llm_chat_hdr_guid}"
    )
    proactivity=True
    affective_dialog=True
    APP_NAME = appName
    await websocket.accept()
    logger.debug("WebSocket connection accepted")
    model_name = agent.model
    is_native_audio = "native-audio" in model_name.lower()
    if is_native_audio:
        # Native audio models require AUDIO response modality
        # with audio transcription
        response_modalities = [types.Modality.AUDIO]

        # Build RunConfig with optional proactivity and affective dialog
        # These features are only supported on native audio models
        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=response_modalities,
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            session_resumption=types.SessionResumptionConfig(),
            proactivity=(
                types.ProactivityConfig(proactive_audio=True)
                if proactivity
                else None
            ),
            enable_affective_dialog=affective_dialog
            if affective_dialog
            else None,
        )
        logger.debug(
            f"Native audio model detected: {model_name}, "
            f"using AUDIO response modality, "
            f"proactivity={proactivity}, affective_dialog={affective_dialog}"
        )
    else:
        # Half-cascade models support TEXT response modality
        # for faster performance
        response_modalities = [types.Modality.TEXT]
        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=response_modalities,
            input_audio_transcription=None,
            output_audio_transcription=None,
            session_resumption=types.SessionResumptionConfig(),
        )
        logger.debug(
            f"Half-cascade model detected: {model_name}, "
            "using TEXT response modality"
        )
        
    logger.debug(f"RunConfig created: {run_config}")

    # Build initial session state from context identifiers
    initial_state = {}
    if user_guid:
        initial_state["user_guid"] = user_guid
    if library_hdr_guid:
        initial_state["library_hdr_guid"] = library_hdr_guid
    if notebook_hdr_guid:
        initial_state["notebook_hdr_guid"] = notebook_hdr_guid
    if llm_chat_hdr_guid:
        initial_state["llm_chat_hdr_guid"] = llm_chat_hdr_guid
    if focus_session_guid:
        initial_state["focus_session_guid"] = focus_session_guid

    # Get or create session (handles both new sessions and reconnections)
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    if not session:
        await session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id,
            state=initial_state if initial_state else None,
        )
    elif initial_state:
        # Update existing session state with new context values
        session.state.update(initial_state)

    live_request_queue = LiveRequestQueue()

    # ========================================
    # Phase 2.5: Inject initial reading context into the live session
    # ========================================
    # Build and send the socratic agent context (book title, recent conversation,
    # session notes) as a text Content message. The model sees this as grounding
    # material before any audio arrives.
    def _inject_reading_context() -> None:
        """Build reading context and inject it into the LiveRequestQueue."""
        try:
            context_text = build_socratic_agent_context(
                focus_session_guid=focus_session_guid,
                library_hdr_guid=library_hdr_guid,
            )
            if context_text:
                context_content = types.Content(
                    parts=[types.Part(text=f"[Reading Context Update]\n{context_text}")]
                )
                live_request_queue.send_content(context_content)
                logger.debug(f"Injected reading context ({len(context_text)} chars) into live session")
            else:
                logger.debug("No reading context available to inject")
        except Exception as e:
            logger.error(f"Failed to inject reading context: {e}", exc_info=True)

    _inject_reading_context()

    # ========================================
    # Phase 3: Active Session (concurrent bidirectional communication)
    # ========================================

    async def upstream_task() -> None:
        """Receives messages from WebSocket and sends to LiveRequestQueue."""
        logger.debug("upstream_task started")
        try:
            while True:
                # Receive message from WebSocket (text or binary)
                message = await websocket.receive()

                # Handle binary frames (audio data)
                if "bytes" in message:
                    audio_data = message["bytes"]
                    logger.debug(
                        f"Received binary audio chunk: {len(audio_data)} bytes"
                    )

                    audio_blob = types.Blob(
                        mime_type="audio/pcm;rate=16000", data=audio_data
                    )
                    live_request_queue.send_realtime(audio_blob)

                # Handle text frames (JSON messages)
                elif "text" in message:
                    text_data = message["text"]
                    logger.debug(f"Received text message: {text_data[:100]}...")

                    json_message = json.loads(text_data)

                    # Handle context handshake message — injects context into session state
                    if json_message.get("type") == "context":
                        logger.debug("Received context handshake message")
                        ctx = json_message.get("data", {})
                        current_session = await session_service.get_session(
                            app_name=APP_NAME, user_id=user_id, session_id=session_id
                        )
                        if current_session:
                            for key in ("user_guid", "library_hdr_guid", "notebook_hdr_guid", "llm_chat_hdr_guid"):
                                if ctx.get(key):
                                    current_session.state[key] = ctx[key]
                            logger.debug(f"Session state updated from context message: {ctx}")
                        continue

                    # Handle LLMEvent message — stored in session state for agent context
                    if json_message.get("type") == "event":
                        logger.debug("Received LLMEvent message")
                        current_session = await session_service.get_session(
                            app_name=APP_NAME, user_id=user_id, session_id=session_id
                        )
                        if current_session:
                            current_session.state["llm_event"] = {
                                "event_guid": json_message.get("event_guid"),
                                "event_type": json_message.get("event_type"),
                                "event_context": json_message.get("event_context", []),
                            }
                            logger.debug(
                                f"Session state updated with LLMEvent: "
                                f"event_type={json_message.get('event_type')}, "
                                f"event_guid={json_message.get('event_guid')}"
                            )
                        continue

                    # Extract text from JSON and send to LiveRequestQueue
                    if json_message.get("type") == "text":
                        logger.debug(
                            f"Sending text content: {json_message['text']}"
                        )
                        content = types.Content(
                            parts=[types.Part(text=json_message["text"])]
                        )
                        live_request_queue.send_content(content)

                    # Handle image data
                    elif json_message.get("type") == "image":
                        logger.debug("Received image data")

                        # Decode base64 image data
                        image_data = base64.b64decode(json_message["data"])
                        mime_type = json_message.get("mimeType", "image/jpeg")

                        logger.debug(
                            f"Sending image: {len(image_data)} bytes, "
                            f"type: {mime_type}"
                        )

                        # Send image as blob
                        image_blob = types.Blob(
                            mime_type=mime_type, data=image_data
                        )
                        live_request_queue.send_realtime(image_blob)
                    
                    # Handle control messages
                    elif json_message.get("type") == "control":
                        action = json_message.get("action")
                        logger.debug(f"Received control message: {action}")
                        if action == "end_speech":
                            # In BIDI mode, we don't necessarily need to do anything special for end_speech
                            # as the model detects silence, but we log it.
                            pass
        except Exception as e:
            logger.error(f"Error in upstream_task: {e}", exc_info=True)
            raise


    async def downstream_task() -> None:
        """Receives Events from run_live() and sends to WebSocket."""
        logger.debug("downstream_task started, calling runner.run_live()")
        try:
            logger.debug(
                f"Starting run_live with user_id={user_id}, session_id={session_id}"
            )
            
            # Track turn state to signal message start/stop
            turn_in_progress = False

            # Accumulate transcriptions per turn for fallback persistence.
            # If the agent's save_conversation_turn tool doesn't fire, we
            # persist the turn ourselves when turn_complete is received.
            turn_user_transcription = ""
            turn_assistant_transcription = ""
            agent_saved_this_turn = False
            
            async for event in runner.run_live(
                user_id=user_id,
                session_id=session_id,
                live_request_queue=live_request_queue,
                run_config=run_config,
            ):
                # Map ADK event to frontend message format
                timestamp = datetime.now().isoformat()
                client_messages = []
                
                # Check for turn completion
                is_turn_complete = hasattr(event, "turn_complete") and event.turn_complete
                
                # 0. Input audio transcription (user's speech)
                if hasattr(event, "input_audio_transcription") and event.input_audio_transcription and event.input_audio_transcription.text:
                    # Accumulate user transcription for fallback persistence
                    if event.input_audio_transcription.finished:
                        turn_user_transcription = event.input_audio_transcription.text
                    
                    client_messages.append({
                        "type": "text",
                        "timestamp": timestamp,
                        "content": event.input_audio_transcription.text,
                        "is_final": event.input_audio_transcription.finished,
                        "metadata": {
                            "role": "user",
                            "message_type": "transcription"
                        }
                    })
                
                # 1. Output transcription
                if hasattr(event, "output_transcription") and event.output_transcription and event.output_transcription.text:
                    # Accumulate assistant transcription for fallback persistence
                    if event.output_transcription.finished:
                        turn_assistant_transcription = event.output_transcription.text
                    
                    msg_start = False
                    if not turn_in_progress:
                        turn_in_progress = True
                        msg_start = True
                        
                    client_messages.append({
                        "type": "text",
                        "timestamp": timestamp,
                        "content": event.output_transcription.text,
                        "is_final": event.output_transcription.finished,
                        "metadata": {
                            "role": "assistant",
                            "message_start": msg_start
                        }
                    })

                # 2. Content parts
                if hasattr(event, "content") and event.content and event.content.parts:
                    # Detect which agent produced this event (if available)
                    agent_name = getattr(event, "author", None) or ""
                    if agent_name:
                        logger.info(f"Event authored by agent: {agent_name}")

                    for part in event.content.parts:
                        # Skip "thought" parts (chain of thought / reasoning)
                        if getattr(part, "thought", False):
                            logger.debug("Filtering out model 'thought' part")
                            continue

                        # Handle text part (only if not a thought)
                        if hasattr(part, "text") and part.text:
                            # Double-check this isn't a thought part by checking content
                            # Thoughts often start with ** or contain analysis markers
                            text_content = part.text.strip()
                            if text_content.startswith("**") and "**" in text_content[2:]:
                                logger.debug(f"Filtering out potential thought text: {text_content[:50]}...")
                                continue
                            
                            msg_start = False
                            if not turn_in_progress:
                                turn_in_progress = True
                                msg_start = True

                            # Detect structured JSON responses from specialist agents
                            # (quiz questions, evaluations, pixel art URLs)
                            response_type = "text"
                            structured_data = None
                            try:
                                parsed = json.loads(text_content)
                                if isinstance(parsed, dict):
                                    if "questions" in parsed:
                                        response_type = "quiz_questions"
                                        structured_data = parsed
                                    elif "evaluations" in parsed and "composite_score" in parsed:
                                        response_type = "quiz_evaluation"
                                        structured_data = parsed
                                    elif "pixel_art_url" in parsed or "image_url" in parsed:
                                        response_type = "pixel_art"
                                        structured_data = parsed
                            except (json.JSONDecodeError, TypeError):
                                pass  # Not JSON — treat as plain text

                            metadata = {
                                "role": "assistant",
                                "message_start": msg_start,
                            }
                            if agent_name:
                                metadata["agent_name"] = agent_name
                            if response_type != "text":
                                metadata["response_type"] = response_type

                            client_message = {
                                "type": "text",
                                "timestamp": timestamp,
                                "content": part.text,
                                "is_final": True,
                                "metadata": metadata,
                            }
                            if structured_data is not None:
                                client_message["structured_data"] = structured_data

                            client_messages.append(client_message)
                        
                        # Handle audio part
                        if hasattr(part, "inline_data") and part.inline_data:
                            msg_start = False
                            if not turn_in_progress:
                                turn_in_progress = True
                                msg_start = True
                                
                            audio_base64 = base64.b64encode(part.inline_data.data).decode('utf-8')
                            client_messages.append({
                                "type": "audio",
                                "timestamp": timestamp,
                                "data": audio_base64,
                                "format": "pcm",
                                "sample_rate": 24000, # Google ADK outputs at 24kHz
                                "metadata": {
                                    "role": "assistant",
                                    "message_start": msg_start
                                }
                            })

                # 2.5. Detect agent tool calls — if save_conversation_turn was
                # called by the agent, mark this turn as already persisted so
                # the fallback doesn't duplicate the save.
                if hasattr(event, "content") and event.content and event.content.parts:
                    for part in event.content.parts:
                        # Detect function_call parts (model requesting tool execution)
                        if hasattr(part, "function_call") and part.function_call:
                            if getattr(part.function_call, "name", "") == "save_conversation_turn":
                                agent_saved_this_turn = True
                                logger.debug("Agent called save_conversation_turn (function_call part) — skipping fallback persistence")
                        # Detect function_response parts (tool execution result)
                        if hasattr(part, "function_response") and part.function_response:
                            if getattr(part.function_response, "name", "") == "save_conversation_turn":
                                agent_saved_this_turn = True
                                logger.debug("save_conversation_turn response received — skipping fallback persistence")

                if hasattr(event, "actions") and event.actions:
                    # Check function_calls for save_conversation_turn
                    if hasattr(event, "function_calls") and event.function_calls:
                        for fc in event.function_calls:
                            if getattr(fc, "name", "") == "save_conversation_turn":
                                agent_saved_this_turn = True
                                logger.debug("Agent called save_conversation_turn (event.function_calls) — skipping fallback persistence")

                # Also check for tool-use via get_function_calls pattern
                if hasattr(event, "get_function_calls"):
                    try:
                        fcs = event.get_function_calls()
                        if fcs:
                            for fc in fcs:
                                if getattr(fc, "name", "") == "save_conversation_turn":
                                    agent_saved_this_turn = True
                                    logger.debug("Agent called save_conversation_turn (get_function_calls) — skipping fallback persistence")
                    except Exception:
                        pass

                # 3. Status messages for control
                if is_turn_complete:
                    client_messages.append({
                        "type": "status",
                        "timestamp": timestamp,
                        "status": "completed",
                        "message": "Turn finished"
                    })

                    # Fallback persistence: if the agent did NOT call
                    # save_conversation_turn during this turn, persist the
                    # transcriptions ourselves so no conversation is lost.
                    if not agent_saved_this_turn and (turn_user_transcription or turn_assistant_transcription):
                        # Read the latest llm_chat_hdr_guid from session state
                        # in case it was updated during the session.
                        current_session = await session_service.get_session(
                            app_name=APP_NAME, user_id=user_id, session_id=session_id
                        )
                        effective_chat_hdr_guid = llm_chat_hdr_guid
                        effective_user_guid = user_guid
                        effective_focus_session_guid = focus_session_guid
                        if current_session:
                            effective_chat_hdr_guid = current_session.state.get("llm_chat_hdr_guid", llm_chat_hdr_guid)
                            effective_user_guid = current_session.state.get("user_guid", user_guid)
                            effective_focus_session_guid = current_session.state.get("focus_session_guid", focus_session_guid)

                        _fallback_save_turn(
                            user_guid=effective_user_guid,
                            llm_chat_hdr_guid=effective_chat_hdr_guid,
                            user_message=turn_user_transcription,
                            assistant_message=turn_assistant_transcription,
                            focus_session_guid=effective_focus_session_guid,
                        )

                    # Reset per-turn accumulators for the next turn
                    turn_in_progress = False
                    turn_user_transcription = ""
                    turn_assistant_transcription = ""
                    agent_saved_this_turn = False

                    # Re-inject updated reading context after each turn so the
                    # agent has fresh notes and conversation history for the next
                    # user utterance. This is deterministic — no tool call needed.
                    _inject_reading_context()
                
                # Send all mapped messages
                for msg in client_messages:
                    msg_json = json.dumps(msg)
                    # Truncate debug log for audio data
                    log_msg = msg_json[:150] + "..." if len(msg_json) > 150 else msg_json
                    logger.debug(f"[SERVER -> CLIENT] {log_msg}")
                    await websocket.send_text(msg_json)
                    
            logger.debug("run_live() generator completed")
        except Exception as e:
            logger.error(f"Error in downstream_task: {e}", exc_info=True)
            raise

    # Run both tasks concurrently
    # Exceptions from either task will propagate and cancel the other task
    try:
        logger.debug(
            "Starting asyncio.gather for upstream and downstream tasks"
        )
        await asyncio.gather(upstream_task(), downstream_task())
        logger.debug("asyncio.gather completed normally")
    except WebSocketDisconnect:
        logger.debug("Client disconnected normally")
    except Exception as e:
        logger.error(f"Unexpected error in streaming tasks: {e}", exc_info=True)
    finally:
        # ========================================
        # Phase 4: Session Termination
        # ========================================

        # Always close the queue, even if exceptions occurred
        logger.debug("Closing live_request_queue")
        live_request_queue.close()




    
  