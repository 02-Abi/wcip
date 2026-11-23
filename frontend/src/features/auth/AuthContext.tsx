import { createContext, useCallback, useContext, useMemo, useState } from "react"
import { login as apiLogin, register as apiRegister, type RegisterPayload } from "@/api/auth"
import { tokens } from "@/lib/tokens"

type AuthCtx = {
  isAuthenticated: boolean
  login: (u: string, p: string) => Promise<void>
  signup: (payload: RegisterPayload) => Promise<void>
  logout: () => void
}

const Ctx = createContext<AuthCtx | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setAuth] = useState(tokens.has())

  const login = useCallback(async (u: string, p: string) => {
    const { access, refresh } = await apiLogin(u, p)
    tokens.set(access, refresh)
    setAuth(true)
  }, [])

  const signup = useCallback(async (payload: RegisterPayload) => {
    await apiRegister(payload)
    const { access, refresh } = await apiLogin(payload.username, payload.password)
    tokens.set(access, refresh)
    setAuth(true)
  }, [])

  const logout = useCallback(() => {
    tokens.clear()
    setAuth(false)
  }, [])

  const value = useMemo(
    () => ({ isAuthenticated, login, signup, logout }),
    [isAuthenticated, login, signup, logout],
  )
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useAuth() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>")
  return ctx
}

