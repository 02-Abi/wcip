import type { ButtonHTMLAttributes, ReactNode } from "react"
import { cn } from "@/lib/cn"

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode
  variant?: "primary" | "ghost"
  block?: boolean
}

export function Button({ children, variant = "primary", block, className, ...rest }: Props) {
  return (
    <button
      {...rest}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-lg text-sm font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed",
        variant === "primary" && "bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-2.5 px-4 hover:from-cyan-400 hover:to-blue-500 shadow-lg shadow-blue-600/20",
        variant === "ghost" && "text-slate-300 hover:bg-white/5 px-3 py-2",
        block && "w-full",
        className,
      )}
    >
      {children}
    </button>
  )
}

