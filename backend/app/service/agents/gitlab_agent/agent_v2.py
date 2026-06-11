"""
GitLab Agent V2 — Sequential Multi-Agent Workflow

Uses ADK's SequentialAgent to guarantee all four stages run in order:
  1. Synthesis Agent → 2. Issue Creator → 3. Developer (branch + file) → 4. Merge Request Creator

Each agent's output is stored in session state via output_key and referenced
by downstream agents using {key_name} template syntax.
"""

import os
import logging

from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from service.agents.tools.gitlab_tools import create_branch, create_file, update_file

logger = logging.getLogger(__name__)

# --- Configuration & Auth ---
AI_MODEL = os.getenv("SYNTHESIS_MODEL", "gemini-2.5-flash")
GITLAB_TOKEN = os.environ.get("GITLAB_PERSONAL_ACCESS_TOKEN", "")
TARGET_PROJECT = os.environ.get("GITLAB_PROJECT_ID", "")
DEFAULT_BRANCH = "main" #"test-branch"

# Duplicate OS environment for the MCP Node subprocess
mcp_env = os.environ.copy()
mcp_env.update({
    "GITLAB_PERSONAL_ACCESS_TOKEN": GITLAB_TOKEN,
    "GITLAB_API_URL": "https://gitlab.com/api/v4",
})


# --- MCP Toolset Factory ---
def get_gitlab_mcp_toolset():
    """Creates a fresh MCP toolset instance to avoid STDIO pipe collisions."""
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "mcp-remote@latest", "https://gitlab.com/api/v4/mcp"],
                env=mcp_env,
            ),
            timeout=90,
        ),
    )


# --- Stage 1: Synthesis Agent ---
gl_synthesis_agent = LlmAgent(
    model=AI_MODEL,
    name="gl_synthesis_agent",
    description="Analyzes the user's reading context (notes, transcripts, metadata) to generate issue details, synthesized markdown notes, and MR summaries.",
    instruction="""You are the MonkMark GitLab Synthesis Agent. 
You will receive a JSON context containing a user's reading session data, including book metadata, raw notes, and an AI chat transcript.

Your task is to analyze this data and generate three artifacts for the downstream pipeline:
1. Issue Details: Identify an "intellectual debt" (a concept to explore further or a habit to build) based on the user's transcript and notes. Formulate a concise Title and Description.
2. Atomic Notes: Clean up the messy transcripts and extract key principles into a pristine, structured Markdown format.
3. MR Summary: A short summary of the key concepts added during this session.

Output your response EXACTLY in the following format, with no extra text or markdown code block backticks outside of the sections:

---ISSUE_TITLE---
[Insert Issue Title Here]
---ISSUE_DESCRIPTION---
[Insert Issue Description Here]
---MARKDOWN_NOTES---
# [Insert Book Name] - Reading Notes
[Insert highly structured, synthesized markdown notes here based on the chat and raw notes]
---MR_SUMMARY---
[Insert 1-2 sentences summarizing the integrated knowledge]
""",
    tools=[],
    output_key="synthesis_result",
)


# --- Stage 2: Issue Creator Agent ---
issue_agent = LlmAgent(
    model=AI_MODEL,
    name="issue_creator_agent",
    description="Creates issues in a GitLab project using the official GitLab MCP API.",
    instruction=f"""You are an issue creation agent. Your ONLY job is to create a GitLab issue.

IMPORTANT: When using the create_issue tool, you MUST use the parameter named "id" and set it to "{TARGET_PROJECT}".

Context provided by the Synthesis Agent:
{{synthesis_result}}

Steps:
1. Extract the text immediately following ---ISSUE_TITLE--- as the issue title.
2. Extract the text immediately following ---ISSUE_DESCRIPTION--- (until the next delimiter) as the issue description.
3. Call the create_issue tool with:
   - id: "{TARGET_PROJECT}"
   - title: the extracted title
   - description: the extracted description
4. After the tool returns successfully, output the Issue IID, title, and web URL in this exact format:
   Issue #<IID>: <title>
   URL: <issue_web_url>

RULES:
- Do NOT attempt any file or branch operations.
- Do NOT explain what you cannot do.
- Output ONLY the two lines above after creating the issue (the "Issue #<IID>: <title>" line and the "URL: <url>" line).""",
    tools=[get_gitlab_mcp_toolset()],
    output_key="issue_result",
)


# --- Stage 3: Developer Agent ---
code_agent = LlmAgent(
    model=AI_MODEL,
    name="developer_agent",
    description="Creates branches and commits files to a GitLab repository using the python-gitlab API.",
    instruction=f"""You are a developer agent that creates branches and commits files.

IMPORTANT: When using your tools, always use the parameter named "project_id" and set it to "{TARGET_PROJECT}".
Default source branch: "{DEFAULT_BRANCH}".

Context from previous steps:
Issue Result: {{issue_result}}
Synthesis Context: {{synthesis_result}}

Your task:
1. Extract the issue number from the Issue Result.
2. Extract the markdown content immediately following ---MARKDOWN_NOTES--- (until the next delimiter) from the Synthesis Context.
3. Call create_branch with:
   - project_id: "{TARGET_PROJECT}"
   - branch_name: "feature/reading-session-<IID>" (replace <IID> with the actual issue number)
   - ref_branch: "{DEFAULT_BRANCH}"
4. Call create_file with:
   - project_id: "{TARGET_PROJECT}"
   - file_path: "docs/reading-notes-<IID>.md"
   - content: the extracted markdown content
   - commit_message: "Add synthesized atomic notes - refs #<IID>"
   - branch_name: the branch you just created

After completing both operations, output ONLY the branch name you created.
Format: <branch_name>""",
    tools=[create_branch, create_file, update_file],
    output_key="branch_result",
)


# --- Stage 4: Merge Request Creator Agent ---
mr_agent = LlmAgent(
    model=AI_MODEL,
    name="merge_request_agent",
    description="Creates merge requests in a GitLab project using the official GitLab MCP API.",
    instruction=f"""You create merge requests in GitLab.

IMPORTANT: When using the create_merge_request tool, you MUST use the parameter named "id" and set it to "{TARGET_PROJECT}".
Target branch is always "{DEFAULT_BRANCH}".

Context from previous steps:
- Issue: {{issue_result}}
- Branch: {{branch_result}}
- Synthesis Context: {{synthesis_result}}

Your task:
1. Extract the summary text immediately following ---MR_SUMMARY--- from the Synthesis Context.
2. Create a merge request with:
   - source_branch: the branch name from the branch result above
   - target_branch: "{DEFAULT_BRANCH}"
   - title: "Knowledge Integration: {{issue_result}}"
   - description: "Closes {{issue_result}}\\n\\n**AI Summary:**\\n[Insert extracted MR summary here]"

After creating the merge request, output ONLY the merge request URL.
Format: <merge_request_url>""",
    tools=[get_gitlab_mcp_toolset()],
    output_key="mr_result",
)


# --- Stage 5: Visual Motif Generator ---
visual_motif_agent = LlmAgent(
    model=AI_MODEL,
    name="visual_motif_generator",
    description="Translates technical/philosophical reading summaries into deep visual art motifs.",
    instruction="""You are the Creative Art Director for MonkMark.

Your task is to review the structured notes generated from a user's recent reading session and compress the overarching intellectual themes into a single vivid, high-fidelity visual metaphor.

Context from current session:
{synthesis_result}

Your task:
1. Identify the core philosophical, technical, or psychological conflict explored in the notes.
2. Construct a single-sentence visual description that represents this concept abstractly.
3. Use artistic, atmospheric imagery (e.g., textures, shadows, light beams, geometric patterns).
4. CRITICAL: Avoid any mention of text, books, reading, or smartphones. The description must be purely thematic and suitable for direct injection into a high-end image generation prompt.

Output ONLY the final single-sentence visual motif string. Do not include headers, quotes, or markdown wrappers.""",
    tools=[],
    output_key="visual_motif_result",
)


# --- Root Sequential Agent ---
gitlab_agent_v2 = SequentialAgent(
    name="gitlab_sequential_agent",
    description=(
        "A sequential workflow agent that orchestrates GitLab operations: "
        "synthesizes reading context, creates intellectual debt issues, "
        "commits clean markdown notes to feature branches, opens merge requests, "
        "and generates a visual motif for the session. "
        "All five stages run every time in fixed order."
    ),
    sub_agents=[gl_synthesis_agent, issue_agent, code_agent, mr_agent, visual_motif_agent],
)