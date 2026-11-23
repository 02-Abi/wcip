import { api } from "./client"

export type ProficiencyBand = "BEGINNER" | "INTERMEDIATE" | "ADVANCED" | "EXPERT"

export type SkillBreakdown = {
  skill_id: string
  skill_name: string
  counts: Record<ProficiencyBand, number>
  total: number
}

export type GapRow = {
  skill_id: string
  skill_name: string
  gap_count: number
  total_weight: number
  affected_projects: string[]
}

export type DepartmentCapacity = {
  department_id: string
  department_name: string
  headcount: number
  avg_skills_per_employee: number
  avg_experience_years: number
  verified_skill_pct: number
}

export type Overview = {
  headcount: number
  department_count: number
  project_count: number
  active_project_count: number
  proficiency_by_band: Record<ProficiencyBand, number>
  top_skills: SkillBreakdown[]
  top_gaps: GapRow[]
  departments: DepartmentCapacity[]
}

export async function getOverview(): Promise<Overview> {
  const { data } = await api.get<Overview>("/analytics/overview/")
  return data
}
