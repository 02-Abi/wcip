import { api } from "./client"

export type LoginResponse = { access: string; refresh: string }
export type RegisterPayload = { username: string; email: string; password: string; password2: string }
export type RegisterResponse = { id: number; username: string; email: string }
export type Me = { id: number; username: string; email: string; is_staff: boolean; is_superuser: boolean }

export async function login(username: string, password: string): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>("/auth/token/", { username, password })
  return data
}

export async function register(payload: RegisterPayload): Promise<RegisterResponse> {
  const { data } = await api.post<RegisterResponse>("/auth/register/", payload)
  return data
}

export async function getMe(): Promise<Me> {
  const { data } = await api.get<Me>("/auth/me/")
  return data
}