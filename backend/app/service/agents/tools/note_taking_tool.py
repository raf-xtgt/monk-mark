# backend/app/service/agents/tools/note_taking_tool.py
# Source: adk-local-docs/docs/tools-custom/function-tools.md
#
# Tools for the note-taking agent. Includes image highlight rendering
# that mirrors the client-side overlay behavior.

import io
import base64
import logging
import tempfile
from typing import Optional

import httpx
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)


def render_highlight_overlay(
    image_url: str,
    highlight_metadata: dict,
) -> dict:
    """Downloads an image and renders highlight overlays matching the client-side behavior.

    Fetches the image from a public URL, draws semi-transparent green rectangles
    at the coordinates specified in highlight_metadata, and returns the composited
    image as a base64-encoded PNG blob along with a temporary file path.

    This mirrors the React Native client rendering:
        backgroundColor: 'rgba(173, 255, 47, 0.3)'
        borderColor: 'rgba(173, 255, 47, 0.8)'
        borderWidth: 2

    Args:
        image_url: Public URL of the source image (e.g. Supabase storage URL).
        highlight_metadata: A dict with a "highlights" key containing a list of
            coordinate objects: [{"x": float, "y": float, "width": float, "height": float}]

    Returns:
        dict with:
            - status: "success" or "error"
            - temp_file_path: Path to the rendered PNG on disk (temporary file)
            - image_base64: Base64-encoded PNG string of the rendered image
            - highlight_count: Number of highlights rendered
        On error:
            - status: "error"
            - error_type: Exception class name
            - message: Error description
    """
    try:
        highlights = highlight_metadata.get("highlights", [])

        if not highlights:
            return {
                "status": "error",
                "message": "No highlights provided in highlight_metadata.",
            }

        # 1. Download the image
        logger.info(f"Downloading image from: {image_url}")
        response = httpx.get(image_url, timeout=30.0, follow_redirects=True)
        response.raise_for_status()

        # 2. Open with Pillow
        image = Image.open(io.BytesIO(response.content)).convert("RGBA")
        logger.info(f"Image loaded: {image.size[0]}x{image.size[1]}")

        # 3. Create a transparent overlay layer for the highlights
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Highlight colors matching the client:
        # Fill: rgba(173, 255, 47, 0.3) → (173, 255, 47, 76)  [0.3 * 255 ≈ 76]
        # Border: rgba(173, 255, 47, 0.8) → (173, 255, 47, 204) [0.8 * 255 ≈ 204]
        fill_color = (173, 255, 47, 76)
        border_color = (173, 255, 47, 204)
        border_width = 2

        for highlight in highlights:
            x = float(highlight.get("x", 0))
            y = float(highlight.get("y", 0))
            width = float(highlight.get("width", 0))
            height = float(highlight.get("height", 0))

            if width <= 0 or height <= 0:
                logger.warning(f"Skipping invalid highlight: {highlight}")
                continue

            # Draw filled rectangle (semi-transparent green)
            left = x
            top = y
            right = x + width
            bottom = y + height

            draw.rectangle(
                [(left, top), (right, bottom)],
                fill=fill_color,
            )

            # Draw border (2px green stroke)
            for i in range(border_width):
                draw.rectangle(
                    [(left + i, top + i), (right - i, bottom - i)],
                    outline=border_color,
                )

        # 4. Composite the overlay onto the original image
        composited = Image.alpha_composite(image, overlay)

        # Convert to RGB for PNG output (drop alpha for compatibility)
        output_image = composited.convert("RGB")

        # 5. Save to a temporary file
        temp_file = tempfile.NamedTemporaryFile(
            suffix=".png", prefix="highlight_render_", delete=False
        )
        output_image.save(temp_file, format="PNG")
        temp_file_path = temp_file.name
        temp_file.close()

        logger.info(
            f"Rendered {len(highlights)} highlight(s) to: {temp_file_path}"
        )

        # 6. Also produce a base64-encoded version for direct use
        buffer = io.BytesIO()
        output_image.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return {
            "status": "success",
            "temp_file_path": temp_file_path,
            "image_base64": image_base64,
            "highlight_count": len(highlights),
            "image_width": output_image.size[0],
            "image_height": output_image.size[1],
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to download image: HTTP {e.response.status_code}", exc_info=True)
        return {
            "status": "error",
            "error_type": "HTTPStatusError",
            "message": f"Failed to download image: HTTP {e.response.status_code}",
        }
    except Exception as e:
        logger.error(f"render_highlight_overlay error: {e}", exc_info=True)
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e),
        }
