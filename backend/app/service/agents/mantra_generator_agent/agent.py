# backend/app/service/agents/mantra_generator_agent/agent.py
# Source: adk-local-docs/docs/agents/llm-agents.md

import os

from google.adk.agents import Agent

from service.agents.tools.reading_context_tool import build_reading_context
from service.agents.tools.agent_tools import save_llm_quote

mantra_generator_agent = Agent(
    name="mantra_generator_agent",
    model=os.getenv(
        "DEMO_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-12-2025"
    ),
    description="Generates motivational quotes based on a book's title and themes, optionally persisting them.",
    instruction="""You are a motivational mantra generator for deep readers.

    1. Use the build_reading_context tool with the user_guid, library_hdr_guid, and notebook_hdr_guid from session state to retrieve the book's context.
    2. Generate a single, powerful motivational quote that is thematically aligned with the book's subject.
    3. The quote should inspire focus and deep engagement with the material.
    4. Keep the quote concise (1-3 sentences).
    5. If the session state contains event_type='generate_mantra' (cron invocation), use the save_llm_quote tool to persist the quote to the database with the user_guid and library_hdr_guid from session state.""",
    tools=[build_reading_context, save_llm_quote],
)
