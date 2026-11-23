import type { ReactNode } from "react"
import { cn } from "@/lib/cn"

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn("glass rounded-2xl p-5", className)}>
      {children}
    </div>
  )
}

