"use client"

import { ShieldQuestion } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

export function HilSoftStrip({
  prompt,
  onApprove,
  onDismiss,
  className,
}: {
  prompt: string
  onApprove: () => void
  onDismiss: () => void
  className?: string
}) {
  return (
    <div
      className={cn(
        "border-amber-500/35 bg-amber-500/10 mx-3 flex flex-col gap-2 rounded-lg border px-3 py-2 sm:mx-4 sm:flex-row sm:items-center sm:gap-3",
        className
      )}
    >
      <div className="text-foreground flex min-w-0 flex-1 items-start gap-2 text-xs leading-snug sm:text-sm">
        <ShieldQuestion
          className="text-amber-700 dark:text-amber-400 mt-0.5 size-4 shrink-0"
          aria-hidden
        />
        <p>{prompt}</p>
      </div>
      <div className="flex shrink-0 flex-wrap gap-1.5 sm:justify-end">
        <Button type="button" size="sm" variant="secondary" onClick={onApprove}>
          Đồng ý
        </Button>
        <Button type="button" size="sm" variant="outline" onClick={onDismiss}>
          Không áp dụng
        </Button>
      </div>
    </div>
  )
}
