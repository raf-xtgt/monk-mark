from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import asyncio
import logging
import sys
import time
from httpx import RemoteProtocolError
from controller.user.app_mm_user_controller import router as user_router
from controller.library.app_mm_library_hdr_controller import router as library_router
from controller.notebook.app_mm_notebook_hdr_controller import router as notebook_router
from controller.notebook.app_mm_notebook_content_controller import router as notebook_content_router
from controller.notebook.app_mm_notebook_content_file_link_controller import router as notebook_content_file_link_router
from controller.notebook.app_mm_notebook_llm_chat_hdr_controller import router as notebook_llm_chat_hdr_router
from controller.notebook.app_mm_notebook_llm_chat_transcript_controller import router as notebook_llm_chat_transcript_router
from controller.file.app_mm_file_upload_controller import router as file_upload_router
from controller.focus_session.app_mm_focus_session_controller import router as focus_session_router
from controller.context.context_controller import router as context_router
from controller.agent_trigger.agent_trigger_controller import router as agent_trigger_router
from controller.reward.app_mm_reward_hdr_controller import router as reward_hdr_router
from controller.dashboard.dashboard_controller import router as dashboard_router
from controller.reward.app_mm_reward_line_controller import router as reward_line_router
from service.websocket.websocket_conn import voice_tutor_endpoint
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from service.agents.socratic_dialogue_agent.agent import socratic_dialogue_agent

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('monk_mark_api.log')
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Monk Mark Web Application Service")

@app.middleware("http")
async def retry_protocol_errors_middleware(request: Request, call_next):
    """
    This middleware will intercept any incoming request to your API, run it, 
    and if a RemoteProtocolError happens anywhere deep in your service layer during that request, 
    it will seamlessly catch it and retry the entire operation.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Try to process the REST API endpoint route
            response = await call_next(request)
            return response
        except RemoteProtocolError as e:
            if attempt == max_retries - 1:
                logger.error(f"Global Retry failed after {max_retries} attempts due to RemoteProtocolError.")
                raise e  # Let it bubble up if we exhausted retries
            
            logger.warning(f"Caught RemoteProtocolError mid-flight. Retrying endpoint execution (Attempt {attempt + 1}/{max_retries})...")
            time.sleep(0.5) # Short grace period before trying the network pool again


logger.info("Monk Mark API starting up...")

APP_NAME = "monk-mark-ws"
session_service = InMemorySessionService()
runner = Runner(app_name=APP_NAME, agent=socratic_dialogue_agent, session_service=session_service)

# Separate runners for REST-triggered agent calls (text-based, non-streaming)
APP_NAME_TEXT = "monk-mark-text"
text_session_service = InMemorySessionService()
from service.agents.art_generator_agent.agent import art_generator_agent as _art_agent
from service.agents.art_generator_agent.agent import art_evolution_agent as _art_evolution_agent
from service.agents.gitlab_agent.agent import gitlab_agent as _gitlab_agent
from service.agents.gitlab_agent.agent_v2 import gitlab_agent_v2 as _gitlab_agent_v2
from service.agents.note_taking_agent.agent import note_taking_agent as _note_taking_agent
from service.agents.milestone_quote_agent.agent import milestone_quote_agent as _milestone_quote_agent

# Registry of text-based runners keyed by event_type
text_runners = {}

def _build_text_runner(agent, app_name_suffix: str) -> Runner:
    """Create a Runner for a text-based agent."""
    return Runner(app_name=f"{APP_NAME_TEXT}-{app_name_suffix}", agent=agent, session_service=text_session_service)

text_runners["generate_art"] = _build_text_runner(_art_agent, "art")
text_runners["generate_art_evolution"] = _build_text_runner(_art_evolution_agent, "art-evolution")
text_runners["gitlab_doc"] = _build_text_runner(_gitlab_agent, "gitlab")
text_runners["gitlab_doc_v2"] = _build_text_runner(_gitlab_agent_v2, "gitlab-v2")
text_runners["note_taking"] = _build_text_runner(_note_taking_agent, "note-taking")
text_runners["milestone_quote"] = _build_text_runner(_milestone_quote_agent, "milestone-quote")

# Keep backward-compatible reference
text_runner = text_runners["generate_art"]



# origins = ["http://localhost:3000"]
# Change this to allow all for prototyping
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows any source to access the API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware configured - allowing all origins")

url_prefix = "/api/mm"

# Include routers
app.include_router(user_router, prefix=url_prefix)
app.include_router(library_router, prefix=url_prefix)
app.include_router(notebook_router, prefix=url_prefix)
app.include_router(notebook_content_router, prefix=url_prefix)
app.include_router(notebook_content_file_link_router, prefix=url_prefix)
app.include_router(notebook_llm_chat_hdr_router, prefix=url_prefix)
app.include_router(notebook_llm_chat_transcript_router, prefix=url_prefix)
app.include_router(file_upload_router, prefix=url_prefix)
app.include_router(focus_session_router, prefix=url_prefix)
app.include_router(context_router, prefix=url_prefix)
app.include_router(agent_trigger_router, prefix=url_prefix)
app.include_router(reward_hdr_router, prefix=url_prefix)
app.include_router(dashboard_router, prefix=url_prefix)
app.include_router(reward_line_router, prefix=url_prefix)

logger.info(f"All routers registered with prefix: {url_prefix}")

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Monk mark api running"}

@app.websocket("/ws/voice-tutor")
async def websocket_tutor(websocket: WebSocket):
    """WebSocket endpoint for Nova Sonic voice tutor"""
    logger.info(f"WebSocket connection attempt from: {websocket.client}")
    try:
        await voice_tutor_endpoint(websocket, APP_NAME, socratic_dialogue_agent, runner, session_service)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
        raise

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info("Starting cron scheduler for automated mantra generation")
    # asyncio.create_task(mantra_cron_loop())
    logger.info("Monk Mark API Started Successfully")
    logger.info("WebSocket endpoint: /ws/voice-tutor")
    logger.info("API prefix: /api/mm")
    logger.info("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Monk Mark API shutting down...")
