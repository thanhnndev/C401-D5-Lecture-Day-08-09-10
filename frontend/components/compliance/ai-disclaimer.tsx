"use client"

import * as React from "react"
import { TriangleAlert } from "lucide-react"

import {
  Alert,
  AlertAction,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

const STORAGE_KEY = "c401-d5-ai-disclaimer-dismissed"

export function AiDisclaimer({ className }: { className?: string }) {
  const [hidden, setHidden] = React.useState(false)

  React.useEffect(() => {
    try {
      if (localStorage.getItem(STORAGE_KEY) === "1") setHidden(true)
    } catch {
      /* private mode */
    }
  }, [])

  const dismiss = () => {
    try {
      localStorage.setItem(STORAGE_KEY, "1")
    } catch {
      /* ignore */
    }
    setHidden(true)
  }

  if (hidden) return null

  return (
    <Alert
      className={cn(
        "border-amber-500/35 bg-amber-500/8 text-foreground py-2.5 pr-2 pl-3 sm:pr-3",
        className
      )}
    >
      <TriangleAlert
        className="text-amber-600 dark:text-amber-500"
        aria-hidden
      />
      <AlertTitle className="text-sm font-semibold tracking-tight">
        C401 · D5 — Agents (AI)
      </AlertTitle>
      <AlertDescription className="text-muted-foreground text-xs leading-relaxed sm:text-sm">
        Đầu ra do mô hình AI tạo; <strong className="text-foreground font-medium">có thể sai hoặc thiếu ngữ cảnh</strong>. Không thay thế tư vấn chính thức, pháp lý hay quyết định nội bộ. Hãy{" "}
        <strong className="text-foreground font-medium">đối chiếu tài liệu và quy trình của tổ chức</strong>. Không nhập dữ liệu nhạy cảm / bí mật nếu chưa được phép.
      </AlertDescription>
      <AlertAction>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="text-muted-foreground h-7 text-xs"
          onClick={dismiss}
        >
          Đã hiểu, ẩn
        </Button>
      </AlertAction>
    </Alert>
  )
}
