import { api } from "./client"

export type EmployeeSkill = {
  id: string
  skill: string
  skill_name: string
  category_name: string
  proficiency: string
  years_experience: number
  is_verified: boolean
}

export async function getEmployeeSkills(employeeId: string) {
  const { data } = await api.get<any>(`/employee-skills/?employee=${employeeId}`)
  return data.results ? data.results : data
}

export async function addEmployeeSkill(employeeId: string, payload: { skill: string; proficiency: string; years_experience: number; is_verified: boolean }) {
  const { data } = await api.post(`/employee-skills/`, { employee: employeeId, ...payload })
  return data
}

export async function updateEmployeeSkill(id: string, payload: Partial<{ proficiency: string; years_experience: number; is_verified: boolean }>) {
  const { data } = await api.patch(`/employee-skills/${id}/`, payload)
  return data
}

export async function deleteEmployeeSkill(id: string) {
  await api.delete(`/employee-skills/${id}/`)
}