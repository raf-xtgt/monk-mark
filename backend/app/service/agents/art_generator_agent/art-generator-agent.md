# MonkMark: Legacy Art Generation System

This document describes the multi-agent architecture for the **Legacy Art** feature within the MonkMark ecosystem. The system uses the **Google Agent Development Kit (ADK)** workflow agents to orchestrate a pipeline that transforms reading reflections into animated visual metaphors.

---

## 1. Architecture Overview

The system uses a hierarchical multi-agent structure built on ADK's `SequentialAgent` and `LoopAgent` primitives. Each stage — synthesis, rendering, animation, critique, and storage — is handled by a dedicated `LlmAgent`, with deterministic workflow agents controlling execution order and iteration.

### Core Agents & Models

| Agent | Role | Model |
| --- | --- | --- |
| **ArtGateAgent** | Validates quiz eligibility before pipeline runs | `imagen-4.0-generate-001` (env: `DEMO_AGENT_MODEL`) |
| **SynthesisAgent** | Extracts core emotional metaphors from user reading logs | `gemma-4-26b-a4b-it-maas` (env: `REASONER_MODEL`) |
| **ImagingAgent** | Translates metaphors into high-resolution static artwork via Imagen 4 | `imagen-4.0-generate-001` (env: `DEMO_AGENT_MODEL`) |
| **MotionAgent** | Animates the static artwork into looping cinemagraphs via Veo | `veo-3.1-generate-001` (env: `DEMO_AGENT_MODEL`) |
| **ArtCriticAgent** | Evaluates output against the initial metaphor and quality bar | `gemini-2.5-flash` (env: `CRITIC_MODEL`) |
| **ArtRefinerAgent** | Refines the metaphor prompt based on critic feedback or exits the loop | `imagen-4.0-generate-001` (env: `DEMO_AGENT_MODEL`) |
| **ArtStorageAgent** | Persists final assets to Supabase Storage | `gemini-2.5-flash` (env: `DEMO_AGENT_MODEL`) |

### Agent Hierarchy

```
art_generator_agent (SequentialAgent)
│   before_agent_callback: validate_quiz_score
│
├── ArtGateAgent (LlmAgent)
│       Blocks pipeline if quiz score < 5.0
│
├── SynthesisAgent (LlmAgent, Gemma 4)
│       Calls build_reading_context → outputs visual_metaphor_prompt
│
├── ArtRefinementLoop (LoopAgent, max_iterations=3)
│   ├── VisualPipeline (SequentialAgent)
│   │   ├── ImagingAgent (LlmAgent) → generate_legacy_art_image tool
│   │   └── MotionAgent (LlmAgent) → generate_legacy_art_animation tool
│   ├── ArtCriticAgent (LlmAgent) → evaluates quality, can call exit_loop
│   └── ArtRefinerAgent (LlmAgent) → refines prompt or calls exit_loop
│
└── ArtStorageAgent (LlmAgent)
        Calls upload_file_to_storage → outputs pixel_art_url
```

---

## 2. Session State Flow

Agents communicate through ADK session state using `output_key`. Each agent writes its result to a named state key that downstream agents read via `{key}` template syntax in their instructions.

| State Key | Written By | Read By |
| --- | --- | --- |
| `quiz_evaluation` | quiz_evaluator_agent (upstream) | validate_quiz_score callback |
| `pipeline_blocked` | validate_quiz_score callback | ArtGateAgent |
| `block_reason` | validate_quiz_score callback | ArtGateAgent |
| `composite_score` | validate_quiz_score callback | SynthesisAgent |
| `visual_metaphor_prompt` | SynthesisAgent / ArtRefinerAgent | ImagingAgent, MotionAgent, ArtCriticAgent, ArtRefinerAgent |
| `generated_image` | ImagingAgent | MotionAgent, ArtCriticAgent, ArtStorageAgent |
| `generated_animation` | MotionAgent | ArtCriticAgent, ArtStorageAgent |
| `art_critique` | ArtCriticAgent | ArtRefinerAgent |
| `pixel_art_url` | ArtStorageAgent | caller (REST trigger response) |

---

## 3. Tools

| Tool | File | Used By | Purpose |
| --- | --- | --- | --- |
| `build_reading_context` | `tools/reading_context_tool.py` | SynthesisAgent | Retrieves book metadata, notes, highlights, and chat history from Supabase |
| `generate_legacy_art_image` | `tools/legacy_art_imaging_tool.py` | ImagingAgent | Calls Imagen 4 API (`imagen-4.0-generate-preview-06-06`) to produce a static painting |
| `generate_legacy_art_animation` | `tools/legacy_art_motion_tool.py` | MotionAgent | Calls Veo API (`veo-2.0-generate-001`) to animate the image into a 5s cinemagraph |
| `upload_file_to_storage` | `tools/agent_tools.py` | ArtStorageAgent | Persists the final asset to Supabase Storage |
| `exit_loop` | Defined inline in `agent.py` | ArtCriticAgent, ArtRefinerAgent | Signals `LoopAgent` termination via `tool_context.actions.escalate = True` |

---

## 4. Workflow Execution Logic

### 4.1 Pre-Pipeline Validation

The `before_agent_callback` (`validate_quiz_score`) runs before any sub-agent:

1. Reads `quiz_evaluation` from session state.
2. Parses `composite_score` (handles both dict and JSON string formats).
3. If score < 5.0 or missing → sets `pipeline_blocked = True` with an encouragement message.
4. If score ≥ 5.0 → sets `pipeline_blocked = False` and stores `composite_score`.

### 4.2 Gate Check

`ArtGateAgent` reads `pipeline_blocked` from state:
- **Blocked:** Relays the `block_reason` message warmly to the user. Pipeline stops here.
- **Not blocked:** Outputs "PROCEED" and the sequential pipeline continues.

### 4.3 Metaphor Synthesis

`SynthesisAgent` (Gemma 4):
1. Calls `build_reading_context` with user/library/notebook GUIDs from session state.
2. Analyzes themes, emotional resonance, symbols, and engagement depth.
3. Outputs a 200–400 word visual metaphor prompt describing composition, palette, lighting, mood, and symbolic elements.
4. Result stored in state as `visual_metaphor_prompt`.

### 4.4 Iterative Generation (Quality Control Loop)

The `ArtRefinementLoop` (`LoopAgent`, max 3 iterations) runs:

**Each iteration:**

1. **VisualPipeline** (SequentialAgent):
   - `ImagingAgent` reads `visual_metaphor_prompt` → calls `generate_legacy_art_image` → stores result in `generated_image`
   - `MotionAgent` reads `visual_metaphor_prompt` + `generated_image` → calls `generate_legacy_art_animation` → stores result in `generated_animation`

2. **ArtCriticAgent** evaluates against 4 criteria:
   - Metaphor adherence
   - Aesthetic quality
   - Animation subtlety
   - Technical success (both tools returned `status: success`)
   
   Outputs either:
   - `"APPROVED: Quality threshold met."` — signals approval
   - Specific constructive feedback for refinement

3. **ArtRefinerAgent** reads the critique:
   - If approved → calls `exit_loop` tool (sets `escalate = True`, breaking the loop)
   - If feedback → refines the `visual_metaphor_prompt` and overwrites state for the next iteration

**Loop terminates when:**
- `exit_loop` is called (quality approved), OR
- `max_iterations` (3) is reached

### 4.5 Storage

`ArtStorageAgent`:
1. Reads `generated_animation` and `generated_image` from state.
2. Prefers the animation (video/mp4); falls back to static image (image/png).
3. Calls `upload_file_to_storage` with user_guid, file metadata, and bucket info.
4. Outputs the asset URL as JSON to `pixel_art_url` state key.

---

## 5. Environment Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `DEMO_AGENT_MODEL` | `imagen-4.0-generate-001` | Model for ImagingAgent, MotionAgent, ArtRefinerAgent, ArtGateAgent |
| `REASONER_MODEL` | `gemma-4-26b-a4b-it-maas` | Model for SynthesisAgent (metaphor extraction) |
| `CRITIC_MODEL` | `gemini-2.5-flash` | Model for ArtCriticAgent (quality evaluation) |

---

## 6. Sequence Diagram

```
Coordinator                    art_generator_agent (Sequential)
    │
    │── delegate ──────────────▶│
    │                           │── validate_quiz_score (callback)
    │                           │
    │                           │── ArtGateAgent
    │                           │   (checks pipeline_blocked)
    │                           │
    │                           │── SynthesisAgent (Gemma 4)
    │                           │   ├── build_reading_context → Supabase
    │                           │   └── outputs visual_metaphor_prompt
    │                           │
    │                           │── ArtRefinementLoop (max 3 iterations)
    │                           │   │
    │                           │   │── VisualPipeline
    │                           │   │   ├── ImagingAgent → Imagen 4 API
    │                           │   │   └── MotionAgent → Veo API
    │                           │   │
    │                           │   │── ArtCriticAgent
    │                           │   │   └── evaluates quality
    │                           │   │
    │                           │   │── ArtRefinerAgent
    │                           │   │   ├── exit_loop (if approved)
    │                           │   │   └── refine prompt (if feedback)
    │                           │   │
    │                           │   └── [loop or exit]
    │                           │
    │                           │── ArtStorageAgent
    │                           │   └── upload_file_to_storage → Supabase
    │                           │
    │◀── pixel_art_url ─────────│
```

---

## 7. Key Architectural Patterns

### Workflow Agents for Deterministic Control

Unlike the conceptual spec which used `Criteria` for termination, the implementation uses ADK's actual `LoopAgent` with `max_iterations` and an `exit_loop` tool that sets `tool_context.actions.escalate = True`. This is the documented ADK pattern for breaking out of loops.

### Output Key Chaining

Each agent writes to a specific state key via `output_key`. Downstream agents read these values through `{key}` template interpolation in their instructions. This avoids passing large payloads through function arguments and prevents LLM hallucination of identifiers.

### Before-Agent Callback for Validation

The `validate_quiz_score` callback runs before the `SequentialAgent` starts any sub-agent, providing a clean gate mechanism without requiring an LLM call for simple threshold checks.

### Graceful Degradation

- If animation generation fails but image succeeds, the storage agent uploads the static image.
- If the loop exhausts all 3 iterations without critic approval, the last generated assets are still stored (best-effort output).
- If quiz evaluation is missing or below threshold, the user receives an encouraging message without wasting compute on generation.

---

## 8. File Reference

```
backend/app/service/agents/art_generator_agent/
├── __init__.py                         # Exports art_generator_agent
├── agent.py                            # Full multi-agent pipeline definition
└── art-generator-agent.md              # This documentation

backend/app/service/agents/tools/
├── reading_context_tool.py             # build_reading_context
├── legacy_art_imaging_tool.py          # generate_legacy_art_image (Imagen 4)
├── legacy_art_motion_tool.py           # generate_legacy_art_animation (Veo)
└── agent_tools.py                      # upload_file_to_storage
```
