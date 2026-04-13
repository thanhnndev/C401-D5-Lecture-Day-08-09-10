import type { AgentNode, ConfidenceLevel, RetrievalChunk } from "@/lib/types/agent-events"

export type UiMessage = {
  id: string
  role: "user" | "assistant"
  content: string
  /** Chỉ assistant: chunk RAG gắn với câu trả lời này (snapshot lúc hoàn thành). */
  sourcesUsed?: RetrievalChunk[]
  /** Route supervisor chọn (snapshot). */
  routeKey?: string
  /** Mức tin cậy tổng hợp cho câu trả lời (snapshot). */
  confidenceLevel?: ConfidenceLevel
}

export type TraceRow =
  | {
      kind: "step"
      stepId: string
      label: string
      node: AgentNode
    }
  | { kind: "route"; route: string; reason: string }
