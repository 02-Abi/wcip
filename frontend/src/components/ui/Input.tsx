import type { InputHTMLAttributes } from "react"
import { cn } from "@/lib/cn"

type Props = InputHTMLAttributes<HTMLInputElement> & { label?: string; error?: string }

export function Input({ label, error, className, ...rest }: Props) {
  return (
    <div>
      {label && <label className="block text-xs uppercase tracking-wider text-slate-300 mb-2">{label}</label>}
      <input
        {...rest}
        className={cn(
          "w-full bg-white/5 border rounded-lg px-3 py-2.5 text-sm placeholder:text-slate-400 outline-none transition",
          error
            ? "border-red-400/60 focus:ring-2 focus:ring-red-400/20"
            : "border-white/10 focus:border-cyan-400/60 focus:ring-2 focus:ring-cyan-400/20",
          className,
        )}
      />
      {error && <p className="mt-1 text-xs text-red-400">{error}</p>}
    </div>
  )
}

