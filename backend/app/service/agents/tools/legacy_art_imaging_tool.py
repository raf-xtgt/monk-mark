# backend/app/service/agents/tools/legacy_art_imaging_tool.py
# Source: adk-local-docs/docs/tools-custom/function-tools.md
# Tool for generating high-fidelity static artwork using Imagen.

import os
import base64
import logging

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")


def generate_legacy_art_image(prompt: str) -> dict:
    """Generates a high-resolution surrealist digital painting from a visual metaphor prompt.

    Calls the Imagen image generation API via Vertex AI to produce a single
    high-fidelity artwork based on the synthesis agent's metaphor description.
    Returns base64-encoded image data on success.

    Args:
        prompt: A detailed visual metaphor description for the artwork to generate.
               Should include themes, emotional tone, and stylistic direction.

    Returns:
        dict with 'status' and either 'image_base64'+'mime_type' or error details.
    """
    try:
        client = genai.Client(
            vertexai=True,
            project=GOOGLE_CLOUD_PROJECT,
            location=GOOGLE_CLOUD_LOCATION,
        )
        response = client.models.generate_images(
            model="imagen-3.0-generate-001",
            prompt=prompt,
            config=types.GenerateImagesConfig(number_of_images=1),
        )

        if response.generated_images:
            image = response.generated_images[0]
            image_b64 = base64.b64encode(image.image.image_bytes).decode("utf-8")
            return {
                "status": "success",
                "image_base64": image_b64,
                "mime_type": "image/png",
            }

        return {
            "status": "error",
            "error_type": "NoImageGenerated",
            "message": "The Imagen API returned no images.",
        }
    except Exception as e:
        logger.error(f"generate_legacy_art_image error: {e}", exc_info=True)
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e),
        }
