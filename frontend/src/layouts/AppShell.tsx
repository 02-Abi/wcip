import { NavLink, Outlet, useNavigate } from "react-router-dom"
import { useAuth } from "@/features/auth/AuthContext"

const NAV = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/employees", label: "Employees" },
  { to: "/skills", label: "Skills" },
  { to: "/projects", label: "Projects" },
  { to: "/analytics", label: "Analytics" },
  { to: "/notifications", label: "Notifications" },
]

export function AppShell() {
  const { logout } = useAuth()
  const nav = useNavigate()

  return (
    <div className="min-h-screen flex bg-[#0B1220] text-white">
      <aside className="w-64 bg-[#0E1628] border-r border-white/10 flex flex-col shadow-2xl z-20">
        <div className="px-6 py-6 border-b border-white/10">
          <div className="text-2xl font-extrabold tracking-tight text-white">
            <span className="text-cyan-400">W</span>CIP
          </div>
          <p className="text-[10px] font-extrabold uppercase tracking-[0.2em] text-cyan-300 mt-1">
            Workforce Intelligence
          </p>
        </div>

        <nav className="flex-1 py-6 px-3 space-y-1">
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              className={({ isActive }) =>
                `block px-4 py-3 rounded-xl text-sm font-bold transition-all duration-200 ${
                  isActive
                    ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-inner"
                    : "text-white hover:text-cyan-300 hover:bg-white/5 border border-transparent"
                }`
              }
            >
              {n.label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-white/10">
          <button
            onClick={() => { logout(); nav("/login", { replace: true }) }}
            className="w-full text-left px-4 py-3 rounded-xl text-sm font-bold text-white hover:text-red-400 hover:bg-red-500/10 transition-colors"
          >
            Sign out
          </button>
        </div>
      </aside>

      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />
        
        <div className="flex-1 overflow-auto p-8 relative z-10">
          <Outlet />
        </div>
      </main>
    </div>
  )
}