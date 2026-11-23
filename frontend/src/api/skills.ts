import { api } from "./client"

export type SkillCategory = {
  id: string
  name: string
  description: string
}

export type Skill = {
  id: string
  name: string
  category: string
  category_name?: string
  is_active: boolean
}

export async function getSkillCategories() {
  const { data } = await api.get<any>("/skill-categories/")
  if (Array.isArray(data)) return data
  if (data && Array.isArray(data.results)) return data.results
  return []
}

export async function createSkillCategory(payload: { name: string; description: string }) {
  const { data } = await api.post("/skill-categories/", payload)
  return data
}

export async function getSkills() {
  const { data } = await api.get<any>("/skills/")
  if (Array.isArray(data)) return data
  if (data && Array.isArray(data.results)) return data.results
  return []
}

export async function createSkill(payload: { name: string; category: string; description: string }) {
  const { data } = await api.post("/skills/", payload)
  return data
}