import os
import logging

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

logger = logging.getLogger(__name__)

# --- Constants ---
AI_MODEL = os.getenv("SYNTHESIS_MODEL", "gemini-2.5-flash")
GITLAB_TOKEN = os.environ.get("GITLAB_PERSONAL_ACCESS_TOKEN", "")

TARGET_PROJECT =  os.environ.get("GITLAB_PROJECT_ID", "")
TARGET_BRANCH = "main"

# Force duplicate the full OS environment context (so node/npm paths carry over)
mcp_env = os.environ.copy()
mcp_env.update({
    "GITLAB_PERSONAL_ACCESS_TOKEN": GITLAB_TOKEN,
    "GITLAB_API_URL": "https://gitlab.com/api/v4"
})

gitlab_agent = Agent(
    model=AI_MODEL,
    name="gitlab_markdown_agent",
    description="An agent that manages markdown files in a GitLab repository using the GitLab MCP server.",
    instruction=f"""You are an agent that manages markdown files in GitLab.

Target project: {TARGET_PROJECT}
Default branch: {TARGET_BRANCH}

IMPORTANT: When calling any GitLab tool, use the parameter name "project_id" (NOT "id") and set its value to "{TARGET_PROJECT}".

Push all markdown files to this project unless told otherwise.

When asked to push a test README file, create a file called README.md with a brief description
of the project and push it to the target repository on the default branch.
Use the create_or_update_file tool with these exact parameters:
- project_id: "{TARGET_PROJECT}"
- file_path: the path of the file (e.g. "README.md")
- content: the file content
- commit_message: a descriptive commit message
- branch: "{TARGET_BRANCH}" """,
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    # Use the official proxy bridging to GitLab's native endpoint
                    args=["-y", "mcp-remote@latest", "https://gitlab.com/api/v4/mcp"], 
                    env=mcp_env,   
                ),
                timeout=90,
            ),
        )
    ],
)