import { api } from "./client"

export type Project = {
  id: string
  name: string
  description: string
  status: string
  priority: string
  start_date: string | null
  end_date: string | null
  headcount_needed: number
}

export type MatchResult = {
  employee_id: string
  employee_name: string
  score: number
  matched_skills: string[]
  missing_skills: string[]
  explanation: string
}

export type Skill = {
  id: string
  name: string
  category: string
}

export async function getProjects() {
  const { data } = await api.get<any>("/projects/")
  if (Array.isArray(data)) return data
  if (data && Array.isArray(data.results)) return data.results
  return []
}

export async function getProject(id: string) {
  const { data } = await api.get<Project>(`/projects/${id}/`)
  return data
}

export async function createProject(payload: any) {
  const { data } = await api.post("/projects/", payload)
  return data
}

export async function getSkills() {
  const { data } = await api.get<any>("/skills/")
  if (Array.isArray(data)) return data
  if (data && Array.isArray(data.results)) return data.results
  return []
}

export async function getRequiredSkills(projectId: string) {
  const { data } = await api.get<any>(`/project-required-skills/?project=${projectId}`)
  if (Array.isArray(data)) return data
  if (data && Array.isArray(data.results)) return data.results
  return []
}

export async function addRequiredSkill(projectId: string, payload: { skill: string; minimum_proficiency: string; minimum_years: number; is_mandatory: boolean; weight: number }) {
  const { data } = await api.post(`/project-required-skills/`, { project: projectId, ...payload })
  return data
}

export async function deleteRequiredSkill(id: string) {
  await api.delete(`/project-required-skills/${id}/`)
}

export async function getProjectMatches(projectId: string) {
  const { data } = await api.get<any>(`/projects/${projectId}/matches/`)
  if (Array.isArray(data)) return data
  if (data && Array.isArray(data.results)) return data.results
  return []
}