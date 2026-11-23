import { useState, type FormEvent } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useAuth } from "./AuthContext"
import { ParallaxHero } from "@/components/ui/ParallaxHero"

export function LoginPage() {
  const { login } = useAuth()
  const nav = useNavigate()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setBusy(true); setError(null)
    try {
      await login(username.trim(), password)
      nav("/", { replace: true })
    } catch {
      setError("Invalid username or password")
    } finally {
      setBusy(false)
    }
  }

  return (
    <ParallaxHero>
      <div className="w-full max-w-md p-8 mx-auto rounded-3xl bg-[#0B1220]/80 backdrop-blur-3xl border border-white/20 shadow-[0_8px_32px_0_rgba(0,0,0,0.8)]">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-extrabold text-white tracking-tight mb-2">
            <span className="text-cyan-400">W</span>CIP
          </h1>
          <p className="text-sm font-bold text-cyan-200 uppercase tracking-widest">
            Smarter People. Stronger Projects.
          </p>
        </div>

        <form onSubmit={onSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-extrabold text-white uppercase tracking-widest mb-2">Username</label>
            <input type="text" className="w-full bg-black/40 border border-white/20 rounded-xl px-4 py-3 text-sm font-semibold text-white placeholder:text-slate-400 outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/50 transition-all"
              placeholder="Enter your username" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </div>
          <div>
            <label className="block text-xs font-extrabold text-white uppercase tracking-widest mb-2">Password</label>
            <input type="password" className="w-full bg-black/40 border border-white/20 rounded-xl px-4 py-3 text-sm font-semibold text-white placeholder:text-slate-400 outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/50 transition-all"
              placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>

          {error && <div className="p-3 rounded-lg bg-red-500/20 border border-red-500/50 text-red-100 font-bold text-xs text-center">{error}</div>}

          <button type="submit" disabled={busy} className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-3.5 rounded-xl font-extrabold text-sm hover:from-cyan-400 hover:to-blue-500 transition-all shadow-lg shadow-cyan-500/40 disabled:opacity-50 mt-4 tracking-wide">
            {busy ? "AUTHENTICATING..." : "SIGN IN"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm font-bold text-white">
          Don't have an account? <Link to="/signup" className="text-cyan-400 hover:text-cyan-300 transition-colors uppercase tracking-wider ml-1">Sign up</Link>
        </p>
      </div>
    </ParallaxHero>
  )
}