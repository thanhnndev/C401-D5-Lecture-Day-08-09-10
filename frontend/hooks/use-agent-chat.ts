"use client"

import * as React from "react"
import { toast } from "sonner"

import { iterateAgentEventsFromResponse } from "@/lib/agent/parse-sse"
import type { AgentNode } from "@/lib/types/agent-events"
import type {
  PipelineMetrics,
  RetrievalChunk,
} from "@/lib/types/agent-events"

export type UiMessage = {
  id: string
  role: "user" | "assistant"
  content: string
}

export type TraceRow =
  | {
      kind: "step"
      stepId: string
      label: string
      node: AgentNode
    }
  | { kind: "route"; route: string; reason: string }

function id() {
  return `m_${Math.random().toString(36).slice(2, 11)}`
}

export function useAgentChat() {
  const [messages, setMessages] = React.useState<UiMessage[]>([])
  const [streamingText, setStreamingText] = React.useState("")
  const [loading, setLoading] = React.useState(false)
  const [traceRows, setTraceRows] = React.useState<TraceRow[]>([])
  const [sources, setSources] = React.useState<RetrievalChunk[]>([])
  const [pipeline, setPipeline] = React.useState<PipelineMetrics | null>(null)
  const [lastTraceId, setLastTraceId] = React.useState<string | undefined>()
  const [grounded, setGrounded] = React.useState<boolean | null>(null)

  const abortRef = React.useRef<AbortController | null>(null)

  const stop = React.useCallback(() => {
    abortRef.current?.abort()
    abortRef.current = null
    setLoading(false)
    setStreamingText((prev) => {
      if (prev.trim()) {
        setMessages((m) => [
          ...m,
          {
            id: id(),
            role: "assistant",
            content: `${prev.trim()}\n\n*(Phản hồi đã dừng theo yêu cầu.)*`,
          },
        ])
      }
      return ""
    })
  }, [])

  const send = React.useCallback(async (text: string) => {
    const trimmed = text.trim()
    if (!trimmed || loading) return

    const userMsg: UiMessage = { id: id(), role: "user", content: trimmed }
    setMessages((m) => [...m, userMsg])
    setStreamingText("")
    setTraceRows([])
    setSources([])
    setPipeline(null)
    setGrounded(null)
    setLastTraceId(undefined)
    setLoading(true)

    const ac = new AbortController()
    abortRef.current = ac

    const nextMessages = [...messages, userMsg].map(({ role, content }) => ({
      role,
      content,
    }))

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: nextMessages }),
        signal: ac.signal,
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(
          typeof err?.error === "string" ? err.error : res.statusText
        )
      }

      let buffer = ""

      for await (const ev of iterateAgentEventsFromResponse(res)) {
        switch (ev.type) {
          case "step_started":
            setTraceRows((rows) => [
              ...rows,
              {
                kind: "step",
                stepId: ev.stepId,
                label: ev.label,
                node: ev.node,
              },
            ])
            break
          case "route_decision":
            setTraceRows((rows) => [
              ...rows,
              { kind: "route", route: ev.route, reason: ev.reason },
            ])
            break
          case "retrieval_result":
            setSources(ev.chunks)
            setGrounded(ev.chunks.length > 0)
            break
          case "token":
            buffer += ev.delta
            setStreamingText(buffer)
            break
          case "pipeline_signal":
            setPipeline(ev.metrics)
            break
          case "error":
            toast.error(ev.message)
            break
          case "done":
            setLastTraceId(ev.traceId)
            break
        }
      }

      if (buffer.trim()) {
        setMessages((m) => [
          ...m,
          { id: id(), role: "assistant", content: buffer },
        ])
      }
      setStreamingText("")
    } catch (e) {
      if (e instanceof DOMException && e.name === "AbortError") {
        return
      }
      const msg = e instanceof Error ? e.message : "Lỗi không xác định"
      toast.error(msg)
    } finally {
      setLoading(false)
      abortRef.current = null
      setStreamingText("")
    }
  }, [loading, messages])

  const copyTraceJson = React.useCallback(async () => {
    const payload = {
      traceId: lastTraceId,
      traceRows,
      sources,
      pipeline,
      grounded,
    }
    try {
      await navigator.clipboard.writeText(JSON.stringify(payload, null, 2))
      toast.success("Đã copy trace JSON")
    } catch {
      toast.error("Không copy được")
    }
  }, [traceRows, sources, pipeline, grounded, lastTraceId])

  return {
    messages,
    streamingText,
    loading,
    traceRows,
    sources,
    pipeline,
    lastTraceId,
    grounded,
    send,
    stop,
    copyTraceJson,
  }
}
