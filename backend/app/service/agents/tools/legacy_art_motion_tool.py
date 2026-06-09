# backend/app/service/agents/tools/legacy_art_motion_tool.py
# Source: adk-local-docs/docs/tools-custom/function-tools.md
# Tool for animating static artwork into looping cinemagraphs using Veo.

import os
import base64
import logging
import time

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")


def generate_legacy_art_animation(
    image_base64: str,
    prompt: str,
) -> dict:
    """Animates a static artwork into a subtle, looping cinemagraph.

    Takes a base64-encoded image and an animation direction prompt, then uses
    the Veo model via Vertex AI to produce a short animated video. Returns
    base64-encoded video data on success.

    Args:
        image_base64: Base64-encoded PNG image data of the static artwork to animate.
        prompt: Animation direction describing the desired motion effects
                (e.g., 'subtle particle drift, gentle light pulsing, atmospheric movement').

    Returns:
        dict with 'status' and either 'video_base64'+'mime_type' or error details.
    """
    try:
        client = genai.Client(
            vertexai=True,
            project=GOOGLE_CLOUD_PROJECT,
            location=GOOGLE_CLOUD_LOCATION,
        )

        # Decode the reference image for the generation request
        image_bytes = base64.b64decode(image_base64)
        reference_image = types.Image(image_bytes=image_bytes, mime_type="image/png")

        # Generate video from image + animation prompt using Veo
        # Veo 3.x supports durations of 4, 6, or 8 seconds
        operation = client.models.generate_videos(
            model="veo-3.0-generate-preview",
            prompt=f"Subtle, looping cinemagraph animation: {prompt}",
            image=reference_image,
            config=types.GenerateVideosConfig(
                number_of_videos=1,
                duration_seconds=4,
            ),
        )

        # Poll for completion — video generation can take 2-3 minutes
        max_wait_seconds = 300
        poll_interval = 10
        elapsed = 0

        while not operation.done and elapsed < max_wait_seconds:
            time.sleep(poll_interval)
            elapsed += poll_interval
            operation = client.operations.get(operation)
            logger.info(f"[Veo] Polling... elapsed={elapsed}s, done={operation.done}")

        if not operation.done:
            return {
                "status": "error",
                "error_type": "Timeout",
                "message": f"Video generation did not complete within {max_wait_seconds}s.",
            }

        # Log the full operation result for debugging
        logger.info(f"[Veo] Operation done. Result: {operation.result}")

        if operation.result and operation.result.generated_videos:
            video = operation.result.generated_videos[0]
            video_bytes = video.video.video_bytes
            video_b64 = base64.b64encode(video_bytes).decode("utf-8")
            return {
                "status": "success",
                "video_base64": video_b64,
                "mime_type": "video/mp4",
            }

        # If no videos returned, check for filtering or other issues
        return {
            "status": "error",
            "error_type": "NoVideoGenerated",
            "message": f"The Veo API returned no video output. Operation result: {operation.result}",
        }
    except Exception as e:
        logger.error(f"generate_legacy_art_animation error: {e}", exc_info=True)
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e),
        }
