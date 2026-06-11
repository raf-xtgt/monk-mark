# backend/app/service/agents/art_generator_agent/agent.py
# Source: adk-local-docs/docs/agents/workflow-agents/sequential-agents.md
# Source: adk-local-docs/docs/agents/workflow-agents/loop-agents.md
#
# Legacy Art Generation System — Multi-agent pipeline that transforms reading
# reflections into visual metaphors using a hierarchical architecture:
#   GateAgent → SynthesisAgent → LoopAgent(ImagingAgent, ArtCriticAgent) → StorageAgent
#
# NOTE: Animation (MotionAgent) is temporarily excluded.
# Backups: agent.py.bak, legacy_art_motion_tool.py.bak

import os
import logging

from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext

from service.agents.tools.reading_context_tool import build_reading_context
from service.agents.tools.legacy_art_imaging_tool import generate_legacy_art_image as _generate_image_raw
from service.agents.tools.art_evolution_tool import fetch_previous_art_metadata

logger = logging.getLogger(__name__)

# --- Constants ---
SYNTHESIS_MODEL = os.getenv("SYNTHESIS_MODEL", "gemini-2.5-flash")
IMAGING_MODEL = os.getenv("IMAGING_MODEL", "gemini-2.5-flash")
CRITIC_MODEL = os.getenv("CRITIC_MODEL", "gemini-2.5-flash")
STATE_QUIZ_EVALUATION = "quiz_evaluation"
STATE_VISUAL_METAPHOR_PROMPT = "visual_metaphor_prompt"
STATE_GENERATED_IMAGE = "generated_image"           # Lightweight status only
STATE_IMAGE_BASE64 = "image_base64_data"            # Raw base64 stored separately (not injected into prompts)
STATE_ART_CRITIQUE = "art_critique"

# Completion signal for the critic
COMPLETION_PHRASE = "APPROVED: Quality threshold met."


# --- Wrapper Tool (stores heavy base64 in state, returns lightweight status) ---
def generate_art_image(prompt: str, tool_context: ToolContext) -> dict:
    """Generates a high-resolution surrealist digital painting from a visual metaphor prompt.

    Calls the image generation API and stores the base64 image data in session state
    for downstream tools. Returns only a lightweight status to avoid token overflow.

    Args:
        prompt: A detailed visual metaphor description for the artwork to generate.
        tool_context: ADK ToolContext (auto-injected) for session state access.

    Returns:
        dict with 'status' and generation details (without the raw base64 data).
    """
    result = _generate_image_raw(prompt)
    if result["status"] == "success":
        # Store heavy base64 in state — NOT in the agent's output_key
        tool_context.state["image_base64_data"] = result["image_base64"]
        return {
            "status": "success",
            "mime_type": result["mime_type"],
            "message": "Image generated successfully. Base64 data stored in session state key 'image_base64_data'.",
        }
    return result


# --- Exit Loop Tool ---
def exit_loop(tool_context: ToolContext):
    """Call this function ONLY when the art critique indicates the artwork meets quality standards and no further iterations are needed."""
    logger.info(
        f"[exit_loop] Triggered by {tool_context.agent_name} — ending refinement loop."
    )
    tool_context.actions.escalate = True
    tool_context.actions.skip_summarization = True
    return {}


# --- Before Agent Callback ---
# NOTE: Hardcoded to always pass with score 5.0 for testing (no quiz implementation yet).
# Production version backed up in: service/agents/tools/validate_quiz_score_tool.py
def validate_quiz_score(callback_context: CallbackContext):
    """Bypasses quiz validation for testing — always sets composite_score to 5.0."""
    callback_context.state["pipeline_blocked"] = False
    callback_context.state["composite_score"] = 5.0
    return None


# --- 1. Synthesis Agent (Safety-Resilient Version) ---
synthesis_agent = LlmAgent(
    name="SynthesisAgent",
    model=SYNTHESIS_MODEL,
    description="Synthesizes a safety-compliant visual prompt for a 2D achievement seal from a visual motif.",
    instruction="""You are the Achievement Illustrator for MonkMark. Your task is to design a 2D "Seal of Deep Focus".

**Input:**
You will receive a visual motif — a single-sentence abstract description of an intellectual theme. Use this as the core concept for your artwork prompt.

**Safety Protocol:**
Avoid any descriptions of physical anatomy, specific clothing, or sensitive symbolic imagery. Focus on artistic style and activity-based silhouettes.

**Process:**
1. Use the visual motif provided in the user message as the thematic foundation.
2. Create a prompt for a 2D, flat-style achievement emblem within a soft Circle or Hexagon border.
3. **Art Content:** Feature a simple, stylized human silhouette or minimalist figure in a focused pose (e.g., sitting with a book, writing at a desk, or in a thoughtful silhouette).
4. **Style:** Use a cozy, boutique bookshop aesthetic—watercolor textures, fine-liner ink, and a warm palette (honey gold, terracotta, sage green).
5. **Instruction for Imagen:** Explicitly state the style is "whimsical, hand-drawn illustration" to avoid photographic/photorealistic triggers.

**Constraints:**
- Prompt must be 100-120 words.
- Focus on the *activity* and the *ornamental border*.
- Incorporate the abstract visual motif into the composition's mood and atmosphere.
- Output ONLY the prompt text. No preamble.""",
    tools=[],
    output_key=STATE_VISUAL_METAPHOR_PROMPT,
)

# --- 2a. Imaging Agent (Inside Refinement Loop) ---
# Generates high-resolution static artwork from the synthesis prompt.
imaging_agent = LlmAgent(
    name="ImagingAgent",
    model=IMAGING_MODEL,
    description="Generates high-resolution surrealist artwork from a visual metaphor prompt.",
    instruction="""You are the Imaging Agent for MonkMark's Legacy Art system.

**Your task:** Generate a high-resolution digital painting based on the visual metaphor prompt.

**Visual Metaphor Prompt:**
{visual_metaphor_prompt}

**Instructions:**
1. Take the visual metaphor prompt above and call the generate_art_image tool with it.
2. If the tool returns successfully, output a brief confirmation (e.g., "Image generated successfully").
3. If the tool returns an error, report the error clearly.

Output ONLY a brief status message. Do NOT include any base64 data in your output.""",
    tools=[generate_art_image],
    output_key=STATE_GENERATED_IMAGE,
)


# --- 2b. Art Critic Agent (Inside Refinement Loop) ---
# Evaluates the generated artwork against the original metaphor and quality standards.
critic_agent = LlmAgent(
    name="ArtCriticAgent",
    model=CRITIC_MODEL,
    description="Evaluates generated artwork for aesthetic quality and metaphor adherence.",
    instruction=f"""You are the Art Critic for MonkMark's Legacy Art quality control system.

**Your task:** Evaluate the generated artwork against the original visual metaphor.

**Original Visual Metaphor Prompt:**
{{visual_metaphor_prompt}}

**Image Generation Status:**
{{generated_image}}

**Evaluation Criteria (ALL must be met for approval):**
1. **Metaphor Adherence:** The visual metaphor prompt is well-suited for artistic rendering
2. **Technical Success:** The image generation status message indicates 'success'
3. **Pipeline Integrity:** No error messages in the generation step

**Task:**
Evaluate against all criteria above.

IF the generation step reported an error status, provide specific feedback on what failed and suggest
the metaphor prompt should be simplified for regeneration.

IF all criteria are met and the image was generated successfully, respond EXACTLY with:
"{COMPLETION_PHRASE}"

IF criteria are NOT fully met but no errors occurred, provide specific constructive feedback
on what to adjust in the visual metaphor prompt for the next iteration.

Either output your critique/feedback OR the exact approval phrase. Nothing else.""",
    tools=[exit_loop],
    output_key=STATE_ART_CRITIQUE,
)


# --- 2c. Refiner Agent (Inside Refinement Loop) ---
# Either exits the loop on approval or refines the metaphor prompt for re-generation.
refiner_agent = LlmAgent(
    name="ArtRefinerAgent",
    model=IMAGING_MODEL,
    description="Refines the visual metaphor prompt based on critic feedback or exits the loop on approval.",
    instruction=f"""You are the Art Refiner for MonkMark's Legacy Art system.

**Current Visual Metaphor Prompt:**
{{visual_metaphor_prompt}}

**Art Critique:**
{{art_critique}}

**Task:**
Analyze the art critique.

IF the critique is EXACTLY "{COMPLETION_PHRASE}":
    You MUST call the 'exit_loop' function immediately. Do not output any text.

ELSE (the critique contains actionable feedback):
    Refine the visual metaphor prompt to address the critic's feedback.
    Output ONLY the refined prompt text — no explanations or preamble.
    Keep the core metaphor intact but adjust composition, style, or detail as suggested.""",
    tools=[exit_loop],
    output_key=STATE_VISUAL_METAPHOR_PROMPT,
)


# --- 3. Quality Control Loop ---
# Iterates: ImagingAgent → Critic → Refiner/Exit
refinement_loop = LoopAgent(
    name="ArtRefinementLoop",
    description="Iteratively generates and refines artwork until quality threshold is met.",
    sub_agents=[imaging_agent, critic_agent, refiner_agent],
    max_iterations=1,
)


# --- 6. Root Art Generator Agent (SequentialAgent) ---
# Orchestrates the full pipeline: Synthesis → Refinement Loop
art_generator_agent = SequentialAgent(
    name="art_generator_agent",
    description="Generates unique Legacy Art rewards based on a visual motif. Uses a multi-agent pipeline: metaphor synthesis → iterative image generation with quality control.",
    sub_agents=[synthesis_agent, refinement_loop],
)


# --- 7. Art Evolution Synthesis Agent ---
# Receives the previous image and visual motif as context from the service layer.
art_evolution_synthesis_agent = LlmAgent(
    name="ArtEvolutionSynthesisAgent",
    model=SYNTHESIS_MODEL,
    description="Visually inspects the previous milestone art and updates its composition using a new visual motif.",
    instruction="""You are the Master Visual Evolution Architect for MonkMark. Your job is to mutate and elevate an existing 2D achievement seal to represent deeper intellectual growth.

You will receive:
1. A direct multimodal visual view of the previous milestone image (attached in your conversation context).
2. The previous evolution tier number.
3. A visual motif — a single-sentence abstract description of the new intellectual theme to integrate.

CRITICAL DIRECTIVES:
- Analyze the layout, style, and core subject matter of the attached historical image.
- You MUST preserve structural continuity: retain the underlying artistic style (e.g., whimsical hand-drawn watercolor aesthetic, dark academic sketch), the central motif silhouette, and core framing elements.
- Mutate and evolve the scene to reflect advanced mastery. Add progressive layers of structural complexity: morph a single candle into an intricate candelabra, introduce detailed filigree or engraving paths along the borders, or evolve a seedling icon into a sturdy sapling root.
- Incorporate the new visual motif's atmosphere and mood into the evolved composition.
- Output ONLY the newly updated, highly descriptive visual metaphor prompt for Imagen (100-120 words). Do not include any meta-commentary or conversational filler.""",
    tools=[],
    output_key=STATE_VISUAL_METAPHOR_PROMPT,
)

# --- 7b. Evolution Pipeline Dedicated Instances ---
# Distinct sub-agent instances to avoid ADK multi-parent validation conflicts.

evolution_imaging_agent = LlmAgent(
    name="EvolutionImagingAgent",
    model=imaging_agent.model,
    description="Generates high-resolution surrealist artwork from an evolved visual metaphor prompt.",
    instruction=imaging_agent.instruction,
    tools=imaging_agent.tools,
    output_key=STATE_GENERATED_IMAGE,
)

evolution_critic_agent = LlmAgent(
    name="ArtEvolutionCriticAgent",
    model=critic_agent.model,
    description="Evaluates evolved artwork for aesthetic quality and metaphor adherence.",
    instruction=critic_agent.instruction,
    tools=critic_agent.tools,
    output_key=STATE_ART_CRITIQUE,
)

evolution_refiner_agent = LlmAgent(
    name="ArtEvolutionRefinerAgent",
    model=refiner_agent.model,
    description="Refines the evolved visual metaphor prompt based on critic feedback or exits the loop on approval.",
    instruction=refiner_agent.instruction,
    tools=refiner_agent.tools,
    output_key=STATE_VISUAL_METAPHOR_PROMPT,
)

evolution_refinement_loop = LoopAgent(
    name="ArtEvolutionRefinementLoop",
    description="Iteratively generates and refines evolved artwork until quality threshold is met.",
    sub_agents=[evolution_imaging_agent, evolution_critic_agent, evolution_refiner_agent],
    max_iterations=1,
)


# --- 8. Root Art Evolution Agent (SequentialAgent) ---
# Handles progressive milestone art mutations using the unique sub-agent pipeline trees.
art_evolution_agent = SequentialAgent(
    name="art_evolution_agent",
    description="Handles progressive milestone art mutations. Receives the previous artwork image and a visual motif, then generates a refined, continuous evolution.",
    sub_agents=[art_evolution_synthesis_agent, evolution_refinement_loop],
)