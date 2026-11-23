import { useEffect, useRef } from "react"
import { useQuery } from "@tanstack/react-query"
import { getOverview, type ProficiencyBand } from "@/api/analytics"
import { Card } from "@/components/ui/Card"

const BANDS: ProficiencyBand[] = ["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"]

const BAND_GRADIENTS: Record<ProficiencyBand, string> = {
  BEGINNER: "from-sky-400 to-cyan-500",
  INTERMEDIATE: "from-cyan-400 to-blue-500",
  ADVANCED: "from-blue-500 to-violet-500",
  EXPERT: "from-violet-500 to-fuchsia-500",
}

const ACCENTS = {
  cyan: { bar: "bg-cyan-400", glow: "shadow-cyan-500/30", ring: "group-hover:ring-cyan-400/40" },
  blue: { bar: "bg-blue-500", glow: "shadow-blue-500/30", ring: "group-hover:ring-blue-400/40" },
  violet: { bar: "bg-violet-500", glow: "shadow-violet-500/30", ring: "group-hover:ring-violet-400/40" },
  emerald: { bar: "bg-emerald-400", glow: "shadow-emerald-500/30", ring: "group-hover:ring-emerald-400/40" },
} as const

type AccentKey = keyof typeof ACCENTS

/** Interactive movie-style 3D background (parallax grid + orbs + starfield). */
function InteractiveBackground() {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    let raf = 0
    const target = { x: 0.5, y: 0.5 }
    const current = { x: 0.5, y: 0.5 }

    const onMove = (e: PointerEvent) => {
      target.x = e.clientX / window.innerWidth
      target.y = e.clientY / window.innerHeight
    }

    const tick = () => {
      current.x += (target.x - current.x) * 0.06
      current.y += (target.y - current.y) * 0.06
      el.style.setProperty("--rx", `${(current.y - 0.5) * -8}deg`)
      el.style.setProperty("--ry", `${(current.x - 0.5) * 12}deg`)
      el.style.setProperty("--tx", `${(current.x - 0.5) * -40}px`)
      el.style.setProperty("--ty", `${(current.y - 0.5) * -30}px`)
      el.style.setProperty("--mx", `${current.x * 100}%`)
      el.style.setProperty("--my", `${current.y * 100}%`)
      raf = requestAnimationFrame(tick)
    }

    window.addEventListener("pointermove", onMove, { passive: true })
    raf = requestAnimationFrame(tick)
    return () => {
      window.removeEventListener("pointermove", onMove)
      cancelAnimationFrame(raf)
    }
  }, [])

  return (
    <div
      ref={ref}
      aria-hidden
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden bg-[#070B14] [perspective:1200px]"
      style={{
        ["--rx" as string]: "0deg",
        ["--ry" as string]: "0deg",
        ["--tx" as string]: "0px",
        ["--ty" as string]: "0px",
        ["--mx" as string]: "50%",
        ["--my" as string]: "50%",
      }}
    >
      {/* cursor-follow nebula */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(600px circle at var(--mx) var(--my), rgba(34,211,238,0.18), transparent 60%)",
        }}
      />
      {/* perspective grid floor */}
      <div
        className="absolute inset-0 opacity-[0.35] will-change-transform"
        style={{
          transform:
            "rotateX(var(--rx)) rotateY(var(--ry)) translate3d(var(--tx), var(--ty), 0)",
          backgroundImage:
            "linear-gradient(rgba(34,211,238,0.12) 1px, transparent 1px), linear-gradient(90deg, rgba(34,211,238,0.12) 1px, transparent 1px)",
          backgroundSize: "44px 44px",
          maskImage: "radial-gradient(ellipse at center, black 30%, transparent 75%)",
          WebkitMaskImage: "radial-gradient(ellipse at center, black 30%, transparent 75%)",
        }}
      />
      {/* floating glow orbs */}
      <div className="absolute inset-0 [transform-style:preserve-3d]">
        <div className="absolute left-[8%] top-[18%] animate-[floatSlow_18s_ease-in-out_infinite]">
          <div
            className="h-[420px] w-[420px] rounded-full blur-3xl opacity-40"
            style={{
              background: "radial-gradient(circle, rgba(34,211,238,0.6), transparent 70%)",
              transform: "translate3d(calc(var(--tx) * 1.4), calc(var(--ty) * 1.4), 40px)",
            }}
          />
        </div>
        <div className="absolute right-[10%] top-[8%] animate-[floatSlow_22s_ease-in-out_infinite_reverse]">
          <div
            className="h-[360px] w-[360px] rounded-full blur-3xl opacity-35"
            style={{
              background: "radial-gradient(circle, rgba(139,92,246,0.55), transparent 70%)",
              transform: "translate3d(calc(var(--tx) * -1.1), calc(var(--ty) * -1.1), 60px)",
            }}
          />
        </div>
        <div className="absolute bottom-[6%] left-[40%] animate-[floatSlow_26s_ease-in-out_infinite]">
          <div
            className="h-[300px] w-[300px] rounded-full blur-3xl opacity-30"
            style={{
              background: "radial-gradient(circle, rgba(16,185,129,0.45), transparent 70%)",
              transform: "translate3d(calc(var(--tx) * 0.8), calc(var(--ty) * 0.8), 80px)",
            }}
          />
        </div>
      </div>
      {/* starfield grain */}
      <div
        className="absolute inset-0 opacity-[0.08] mix-blend-screen"
        style={{
          backgroundImage: "radial-gradient(rgba(255,255,255,0.9) 1px, transparent 1px)",
          backgroundSize: "3px 3px",
        }}
      />
      {/* vignette */}
      <div
        className="absolute inset-0"
        style={{
          background: "radial-gradient(ellipse at center, transparent 45%, rgba(0,0,0,0.55) 100%)",
        }}
      />
    </div>
  )
}

/** 3D depth shell: gradient border + inner highlight + floating shadow + hover lift */
function DepthCard({
  children,
  className = "",
  glow = "shadow-cyan-500/20",
}: {
  children: React.ReactNode
  className?: string
  glow?: string
}) {
  return (
    <div className={`group relative [perspective:1200px] ${className}`}>
      <div
        className={`pointer-events-none absolute inset-0 translate-y-3 rounded-2xl blur-xl opacity-60 ${glow}`}
        aria-hidden
      />
      <div className="relative rounded-2xl bg-gradient-to-b from-white/20 via-white/5 to-transparent p-px shadow-[0_20px_50px_-20px_rgba(0,0,0,0.8)] transition-transform duration-300 ease-out will-change-transform group-hover:-translate-y-1 group-hover:[transform:rotateX(2deg)_rotateY(-2deg)]">
        <div className="relative h-full rounded-[15px] bg-[#0E1628]/95 backdrop-blur-md ring-1 ring-white/10 transition-all duration-300 group-hover:ring-white/20">
          <div className="pointer-events-none absolute inset-x-0 top-0 h-px rounded-t-[15px] bg-gradient-to-r from-transparent via-white/40 to-transparent" aria-hidden />
          {children}
        </div>
      </div>
    </div>
  )
}

function StatCard({
  label,
  value,
  accent = "cyan",
  index = 0,
}: {
  label: string
  value: number | string
  accent?: AccentKey
  index?: number
}) {
  const a = ACCENTS[accent]
  return (
    <DepthCard glow={a.glow} className="animate-[fadeUp_0.5s_ease-out_both]">
      <div style={{ animationDelay: `${index * 80}ms` }} className="p-6">
        <div className="flex items-start justify-between">
          <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-cyan-300/90">
            {label}
          </div>
          <span className={`h-2.5 w-2.5 rounded-full ${a.bar} shadow-[0_0_12px_2px_currentColor]`} />
        </div>
        <div className="mt-3 text-5xl font-black tracking-tight text-white drop-shadow-[0_4px_12px_rgba(0,0,0,0.6)]">
          {value}
        </div>
        <div className="mt-4 h-1 w-full overflow-hidden rounded-full bg-white/5">
          <div className={`h-full w-2/3 rounded-full bg-gradient-to-r ${a.bar.replace("bg-", "from-")} to-transparent opacity-80`} />
        </div>
      </div>
    </DepthCard>
  )
}

export function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["analytics", "overview"],
    queryFn: getOverview,
    refetchOnMount: "always",
    staleTime: 0,
  })

  if (isLoading)
    return (
      <div className="relative">
        <InteractiveBackground />
        <div className="flex items-center gap-3 text-cyan-400 font-bold animate-pulse text-lg">
          <span className="h-3 w-3 rounded-full bg-cyan-400 shadow-[0_0_16px_4px_rgba(34,211,238,0.7)]" />
          Initializing Dashboard...
        </div>
      </div>
    )
  if (error || !data)
    return (
      <div className="relative">
        <InteractiveBackground />
        <div className="text-red-400 font-bold">Failed to load live dashboard data.</div>
      </div>
    )

  const total = Object.values(data.proficiency_by_band).reduce((a, n) => a + n, 0) || 1

  return (
    <div className="relative min-h-screen">
      <InteractiveBackground />
      <div className="relative z-10 space-y-8 max-w-6xl mx-auto [perspective:1500px]">
        <header>
          <h1 className="text-3xl font-extrabold text-white tracking-tight drop-shadow-[0_2px_10px_rgba(34,211,238,0.25)]">
            Dashboard
          </h1>
          <p className="text-cyan-100 font-medium mt-1">
            Live workforce intelligence across the organization.
          </p>
        </header>

        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard label="Total Employees" value={data.headcount} accent="cyan" index={0} />
          <StatCard label="Departments" value={data.department_count} accent="blue" index={1} />
          <StatCard label="Total Projects" value={data.project_count} accent="violet" index={2} />
          <StatCard label="Active Projects" value={data.active_project_count} accent="emerald" index={3} />
        </section>

        <section className="grid lg:grid-cols-2 gap-6">
          <DepthCard>
            <div className="p-6">
              <h2 className="text-lg font-bold mb-6 text-white">Proficiency Distribution</h2>
              <ul className="space-y-5">
                {BANDS.map((b) => {
                  const n = data.proficiency_by_band[b] ?? 0
                  const pct = Math.round((n / total) * 100)
                  return (
                    <li key={b}>
                      <div className="flex justify-between text-sm font-bold mb-2">
                        <span className="text-white uppercase tracking-wider">{b}</span>
                        <span className="text-cyan-400">
                          {n}{" "}
                          <span className="text-slate-300 text-xs font-medium">({pct}%)</span>
                        </span>
                      </div>
                      <div className="h-2.5 bg-white/10 rounded-full overflow-hidden shadow-inner">
                        <div
                          className={`h-full rounded-full bg-gradient-to-r ${BAND_GRADIENTS[b]} shadow-[0_0_12px_rgba(34,211,238,0.5)] transition-[width] duration-700 ease-out`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </li>
                  )
                })}
              </ul>
            </div>
          </DepthCard>

          <DepthCard>
            <div className="p-6">
              <h2 className="text-lg font-bold mb-6 text-white">Top Skills Across Organization</h2>
              <div className="space-y-4">
                {data.top_skills.map((s, i) => (
                  <div
                    key={s.skill_id}
                    className="flex items-center justify-between border-b border-white/10 pb-3 last:border-0 last:pb-0 transition-colors hover:border-cyan-400/30"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-white/15 to-white/5 ring-1 ring-white/15 flex items-center justify-center text-xs font-black text-cyan-300 shadow-[inset_0_1px_0_rgba(255,255,255,0.25)]">
                        #{i + 1}
                      </div>
                      <span className="font-bold text-white">{s.skill_name}</span>
                    </div>
                    <span className="text-sm font-bold text-white bg-white/10 px-3 py-1 rounded-full border border-white/20 shadow-[inset_0_1px_0_rgba(255,255,255,0.15)]">
                      {s.total} emp
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </DepthCard>
        </section>

        <section className="grid lg:grid-cols-2 gap-6">
          <DepthCard glow="shadow-red-500/20">
            <div className="p-6">
              <h2 className="text-lg font-bold mb-6 text-red-400">Critical Project Gaps</h2>
              {data.top_gaps.length === 0 ? (
                <p className="text-sm font-bold text-white">No mandatory gaps detected.</p>
              ) : (
                <ul className="space-y-4">
                  {data.top_gaps.map((g) => (
                    <li
                      key={g.skill_id}
                      className="flex justify-between items-center border-b border-white/10 pb-3 last:border-0"
                    >
                      <span className="font-bold text-white">{g.skill_name}</span>
                      <span className="text-xs font-bold text-red-300 bg-red-500/20 border border-red-500/30 px-2.5 py-1 rounded-md shadow-[0_0_12px_rgba(239,68,68,0.25)]">
                        {g.gap_count} Missing
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </DepthCard>

          <DepthCard>
            <div className="p-6">
              <h2 className="text-lg font-bold mb-6 text-white">Department Capacity</h2>
              <table className="w-full text-sm">
                <thead className="text-cyan-300 border-b-2 border-white/20">
                  <tr>
                    <th className="pb-3 text-left font-bold uppercase tracking-wider">Department</th>
                    <th className="pb-3 text-right font-bold uppercase tracking-wider">Headcount</th>
                    <th className="pb-3 text-right font-bold uppercase tracking-wider">Avg Exp</th>
                  </tr>
                </thead>
                <tbody>
                  {data.departments.map((d) => (
                    <tr
                      key={d.department_id}
                      className="border-b border-white/10 last:border-0 transition-colors hover:bg-white/5"
                    >
                      <td className="py-3 font-bold text-white">{d.department_name}</td>
                      <td className="py-3 text-right font-extrabold text-cyan-400">{d.headcount}</td>
                      <td className="py-3 text-right text-white font-bold">
                        {d.avg_experience_years}{" "}
                        <span className="text-xs text-slate-300">yrs</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </DepthCard>
        </section>
      </div>
    </div>
  )
}