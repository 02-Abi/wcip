import { useMemo, useState, type FormEvent } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useAuth } from "./AuthContext"
import { ParallaxHero } from "@/components/ui/ParallaxHero"

const RULES = [
  { id: "len", label: "8+ Characters", test: (v: string) => v.length >= 8 },
  { id: "num", label: "One Number", test: (v: string) => /\d/.test(v) },
  { id: "alpha", label: "One Letter", test: (v: string) => /[A-Za-z]/.test(v) },
  { id: "special", label: "One Symbol", test: (v: string) => /[^A-Za-z0-9]/.test(v) },
]

export function SignupPage() {
  const { signup } = useAuth()
  const nav = useNavigate()
  const [username, setUsername] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [password2, setPassword2] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const rules = useMemo(() => RULES.map((r) => ({ ...r, ok: r.test(password) })), [password])
  const match = password.length > 0 && password === password2
  const canSubmit = username.trim().length > 0 && email.includes("@") && rules.every((r) => r.ok) && match

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (!canSubmit) { setError("Please satisfy all requirements."); return }
    setBusy(true); setError(null)
    try {
      await signup({ username: username.trim(), email: email.trim(), password, password2 })
      nav("/", { replace: true })
    } catch (err: any) {
      const data = err?.response?.data
      if (data && typeof data === "object") {
        const first = Object.values(data)[0]
        setError(typeof first === "string" ? first : "Signup failed.")
      } else setError("Signup failed. Please try again.")
    } finally {
      setBusy(false)
    }
  }

  return (
    <ParallaxHero>
      <div className="w-full max-w-md p-8 mx-auto rounded-3xl bg-[#0B1220]/80 backdrop-blur-3xl border border-white/20 shadow-[0_8px_32px_0_rgba(0,0,0,0.8)]">
        <div className="text-center mb-6">
          <h1 className="text-4xl font-extrabold text-white tracking-tight mb-2">
            <span className="text-cyan-400">W</span>CIP
          </h1>
          <p className="text-sm font-bold text-cyan-200 uppercase tracking-widest">
            Create your account
          </p>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-extrabold text-white uppercase tracking-widest mb-1">Username</label>
            <input type="text" className="w-full bg-black/40 border border-white/20 rounded-xl px-4 py-2.5 text-sm font-semibold text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/50" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </div>
          <div>
            <label className="block text-xs font-extrabold text-white uppercase tracking-widest mb-1">Email</label>
            <input type="email" className="w-full bg-black/40 border border-white/20 rounded-xl px-4 py-2.5 text-sm font-semibold text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/50" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div>
            <label className="block text-xs font-extrabold text-white uppercase tracking-widest mb-1">Password</label>
            <input type="password" className="w-full bg-black/40 border border-white/20 rounded-xl px-4 py-2.5 text-sm font-semibold text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/50" value={password} onChange={(e) => setPassword(e.target.value)} required />
            <div className="grid grid-cols-2 gap-2 mt-3">
              {rules.map((r) => (
                <div key={r.id} className={`text-[10px] uppercase tracking-wider font-extrabold ${r.ok ? "text-emerald-400" : "text-slate-400"}`}>
                  {r.ok ? "✓" : "○"} {r.label}
                </div>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-xs font-extrabold text-white uppercase tracking-widest mb-1">Confirm Password</label>
            <input type="password" className="w-full bg-black/40 border border-white/20 rounded-xl px-4 py-2.5 text-sm font-semibold text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/50" value={password2} onChange={(e) => setPassword2(e.target.value)} required />
          </div>

          {error && <div className="p-3 rounded-lg bg-red-500/20 border border-red-500/50 text-red-100 font-bold text-xs text-center">{error}</div>}

          <button type="submit" disabled={busy || !canSubmit} className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-3.5 rounded-xl font-extrabold text-sm hover:from-cyan-400 hover:to-blue-500 transition-all shadow-lg shadow-cyan-500/40 disabled:opacity-50 mt-4 tracking-wide">
            {busy ? "CREATING..." : "CREATE ACCOUNT"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm font-bold text-white">
          Already have an account? <Link to="/login" className="text-cyan-400 hover:text-cyan-300 uppercase tracking-wider ml-1">Sign in</Link>
        </p>
      </div>
    </ParallaxHero>
  )
}