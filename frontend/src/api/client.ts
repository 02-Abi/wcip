import axios, { AxiosError, InternalAxiosRequestConfig } from "axios"
import { tokens } from "@/lib/tokens"

const baseURL = (import.meta as any).env.VITE_API_BASE_URL ?? "/api"

export const api = axios.create({ baseURL })

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const t = tokens.access
  if (t && config.headers) config.headers.Authorization = `Bearer ${t}`
  return config
})

let refreshing: Promise<string | null> | null = null

async function refreshAccess(): Promise<string | null> {
  const refresh = tokens.refresh
  if (!refresh) return null
  try {
    const { data } = await axios.post(`${baseURL}/auth/token/refresh/`, { refresh })
    const access = data.access as string
    tokens.set(access)
    return access
  } catch {
    tokens.clear()
    return null
  }
}

api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retried?: boolean }) | undefined
    if (error.response?.status === 401 && original && !original._retried) {
      original._retried = true
      refreshing ??= refreshAccess().finally(() => { refreshing = null })
      const newToken = await refreshing
      if (newToken && original.headers) {
        original.headers.Authorization = `Bearer ${newToken}`
        return api(original)
      }
      if (!location.pathname.startsWith("/login")) location.href = "/login"
    }
    return Promise.reject(error)
  },
)
