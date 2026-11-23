import { api } from "./client"

export type Employee = {
  id: string
  employee_id: string
  first_name: string
  last_name: string
  email: string
  department: string
  department_name?: string
  designation: string
  joining_date: string
  employment_status: string
  total_experience_years: number
}

export type EmployeeListResponse = {
  count: number
  next: string | null
  previous: string | null
  results: Employee[]
}

export async function getEmployees(params: { search?: string; page?: number }) {
  const query = new URLSearchParams()
  if (params.search) query.append("search", params.search)
  if (params.page) query.append("page", params.page.toString())
  
  const { data } = await api.get<EmployeeListResponse>(`/employees/?${query.toString()}`)
  return data
}

export async function getDepartments() {
  const { data } = await api.get<any>("/departments/")
  return data.results ? data.results : data
}

export async function createEmployee(payload: any) {
  const { data } = await api.post("/employees/", payload)
  return data
}

export async function updateEmployee(id: string, payload: any) {
  const { data } = await api.put(`/employees/${id}/`, payload)
  return data
}

export async function deleteEmployee(id: string) {
  await api.delete(`/employees/${id}/`)
}