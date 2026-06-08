from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import asyncio
import logging
import sys
import time
from httpx import RemoteProtocolError

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


logger.info(f"All routers registered with prefix: {url_prefix}")

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Monk mark api running"}


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
