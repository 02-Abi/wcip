import { api } from "./client"

export type SkillAnalytics = {
  by_band: Record<string, number>
  by_skill: Array<{
    skill_id: string
    skill_name: string
    counts: Record<string, number>
    total: number
  }>
}

export type DepartmentAnalytics = {
  department_id: string
  department_name: string
  headcount: number
  avg_skills_per_employee: number
  avg_experience_years: number
  verified_skill_pct: number
}

export async function getSkillsAnalytics(departmentId?: string) {
  const url = departmentId ? `/analytics/skills/?department=${departmentId}` : "/analytics/skills/"
  const { data } = await api.get<SkillAnalytics>(url)
  return data
}

export async function getDepartmentsAnalytics() {
  const { data } = await api.get<{ departments: DepartmentAnalytics[] }>("/analytics/departments/")
  return data.departments
}