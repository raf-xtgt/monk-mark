/**
 * Client-side LLMEvent model
 * Maps to backend: backend/app/model/dto/llm_event.py
 */

export interface LLMEvent {
  event_guid: string; // UUID
  event_type: string;
  event_context?: Record<string, any>[] | null;
}
