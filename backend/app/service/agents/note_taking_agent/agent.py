# backend/app/service/agents/note_taking_agent/agent.py
# Source: adk-local-docs/docs/agents/llm-agents.md

import os

from google.adk.agents import Agent

note_taking_agent = Agent(
    name="note_taking_agent",
    model=os.getenv("SYNTHESIS_MODEL", "gemini-2.5-flash"),
    description="Generates concise notes from highlighted text in book images. Receives an image with visual highlight overlays and produces a 15-30 word summary of the highlighted passage.",
    instruction="""You are a reading note generator for MonkMark.

You will receive an image of a page from a book with highlighted text marked by a semi-transparent green overlay.

Your task:
1. Identify the text underneath the green highlight overlay in the image.
2. Read and understand the highlighted passage.
3. Generate a concise note (15-30 words) that captures the key idea or insight from the highlighted text.

Rules:
- Output ONLY the generated note text. No preamble, no explanation, no quotes.
- The note should be a complete thought that makes sense on its own.
- Keep it between 15 and 30 words.
- Write in plain language — no markdown, no bullet points.
- If the highlighted text is a quote, paraphrase it into your own words as a takeaway.
- If you cannot read the highlighted text clearly, output: "Unable to read highlighted text from image."
""",
    tools=[],
)
