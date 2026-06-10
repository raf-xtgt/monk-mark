# backend/app/service/agents/tools/socratic_thinker_tool.py
import os
import logging

from google import genai
from google.genai import types
from service.agents.tools.agent_context_util import build_socratic_agent_context

logger = logging.getLogger(__name__)

REASONER_MODEL = os.getenv("REASONER_MODEL", "gemini-3.1-flash-lite")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

SOCRATIC_SYSTEM_INSTRUCTION = """You are the cognitive engine of MonkMark's Reading Companion. Your role is to perform deep analysis and generate Socratic responses.

### 1. The Reasoning Protocol (Chain of Thought)
Before responding, evaluate the user's current need. Determine if this is a "Direct Knowledge" moment or a "Socratic Growth" moment:

- **Direct Knowledge (Provide Answers):**
    - The user is asking for a factual definition, a specific quote, or clarification on a complex term.
    - The user is showing signs of frustration or fatigue.
    - The user is asking about the app's functionality.
- **Socratic Growth (Ask Questions):**
    - The user makes a strong assumption or an interpretive claim about the book.
    - The user asks for your "opinion" on a philosophical or moral dilemma presented in the text.

### 2. Response Guidelines
- **Companionable Tone:** Be encouraging and intellectually curious. You are a peer in the user's journey toward intellectual mastery.
- **Nuanced Socratic Dialogue:** When using Socratic questioning, acknowledge their point first, then probe an implication or ask for evidence from their own highlights.
- **Preservationist Respect:** Honor the user's "Digital Margin" (notes and highlights) as sacred references.
- **Conciseness:** Keep responses conversational and suitable for spoken delivery. Do NOT include meta-commentary about your reasoning process.
- **STRICT WORD LIMIT:** Your response MUST be 80 words or fewer. This is a hard constraint — no exceptions. Prioritize clarity and impact over completeness. If a Socratic question is needed, ask ONE focused question. Never exceed 80 words."""


def ask_socratic_thinker(
    user_input: str,
    focus_session_guid: str = "",
    library_hdr_guid: str = "",
) -> dict:
    """Sends the user's question to the Socratic reasoning engine for deep analysis.

    Uses the current focus session context (book title, recent conversation turns,
    and session notes) to ground the reasoning model's response.

    Args:
        user_input: The user's spoken message or question.
        focus_session_guid: UUID of the current focus session (from session state).
        library_hdr_guid: UUID of the library header / book (from session state).

    Returns:
        dict with 'status' and 'response' on success, or error details on failure.
    """
    try:
        # 1. Build focused session context (book title + last 3 turns + session notes)
        reading_context = build_socratic_agent_context(
            focus_session_guid=focus_session_guid if focus_session_guid else None,
            library_hdr_guid=library_hdr_guid if library_hdr_guid else None,
        )

        if not reading_context:
            logger.warning("No reading context available for socratic thinker.")
            reading_context = "No reading context available."

        # 2. Build the prompt with session context
        prompt = f"""## Current Session Context
{reading_context}

## User's Message
{user_input}

Respond thoughtfully based on the session context above. Reference the user's notes and recent conversation when relevant. IMPORTANT: Your response MUST be 80 words or fewer."""

        # 3. Call the reasoner model via Vertex AI
        client = genai.Client(
            vertexai=True,
            project=GOOGLE_CLOUD_PROJECT,
            location="global",
        )

        response = client.models.generate_content(
            model=REASONER_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SOCRATIC_SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=512,
            ),
        )

        if response.text:
            return {
                "status": "success",
                "response": response.text,
            }

        return {
            "status": "error",
            "error_type": "EmptyResponse",
            "message": "The reasoning model returned an empty response.",
        }

    except Exception as e:
        logger.error(f"ask_socratic_thinker error: {e}", exc_info=True)
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e),
        }