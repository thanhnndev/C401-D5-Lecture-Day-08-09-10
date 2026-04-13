"use client"

import type { UiMessage } from "@/lib/types/chat-ui"
import { SourceCard } from "@/components/sources/source-card"

export function MessageSourcesInline({ message }: { message: UiMessage }) {
  if (message.role !== "assistant") return null
  const chunks = message.sourcesUsed
  if (!chunks?.length) return null

  return (
    <div className="border-border bg-muted/25 max-w-[min(100%,52rem)] rounded-lg border px-3 py-2.5 text-sm">
      <p className="text-foreground mb-1.5 text-xs font-semibold tracking-tight">
        Nguồn đã dùng cho câu trả lời này
      </p>
      {message.routeKey ? (
        <p className="text-muted-foreground mb-2 font-mono text-[11px]">
          Route: {message.routeKey}
        </p>
      ) : null}
      <p className="text-muted-foreground mb-2 text-xs leading-relaxed">
        <strong className="text-foreground/90">Cách lấy (demo):</strong> hybrid dense + sparse, rerank
        rồi chọn top chunk theo điểm khớp (hiển thị % trên mỗi đoạn). Luồng thật sẽ nối vector store + policy
        nội bộ.
      </p>
      <ul className="flex flex-col gap-2">
        {chunks.map((c) => (
          <li key={c.id}>
            <SourceCard chunk={c} showRetrievalHint />
          </li>
        ))}
      </ul>
    </div>
  )
}
