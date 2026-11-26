import { api } from "./client"

export type GapReport = {
  coverage_pct: number
  fully_qualified: boolean
  mandatory_gaps: Array<{
    skill_id: string
    skill_name: string
    required_proficiency: string
    required_years: number
    actual_proficiency: string | null
    actual_years: number | null
    status: string
  }>
  optional_gaps: Array<{
    skill_id: string
    skill_name: string
    required_proficiency: string
    required_years: number
    actual_proficiency: string | null
    actual_years: number | null
    status: string
  }>
}

export type Recommendation = {
  rank: number
  skill_name: string
  action_type: string
  reason: string
  estimated_effort_hours: number
  target_proficiency: string
}

export async function getEmployeeGap(employeeId: string, projectId: string) {
  const { data } = await api.get<GapReport>(`/employees/${employeeId}/skill-gap/?project=${projectId}`)
  return data
}

export async function getEmployeeRecommendations(employeeId: string, projectId: string) {
  const { data } = await api.get<{ recommendations: Recommendation[] }>(`/employees/${employeeId}/recommendations/?project=${projectId}`)
  return data.recommendations || []
}