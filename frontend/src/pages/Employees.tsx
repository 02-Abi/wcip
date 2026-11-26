import { useState } from "react"
import { Link } from "react-router-dom"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { getEmployees, getDepartments, createEmployee, updateEmployee, deleteEmployee, type Employee } from "@/api/employees"
import { Card } from "@/components/ui/Card"
import { useAuth } from "@/features/auth/AuthContext"

export function Employees() {
  const { isHR } = useAuth()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState("")
  const [page, setPage] = useState(1)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)

  const [firstName, setFirstName] = useState("")
  const [lastName, setLastName] = useState("")
  const [email, setEmail] = useState("")
  const [department, setDepartment] = useState("")
  const [designation, setDesignation] = useState("")
  const [experience, setExperience] = useState("0")

  const { data, isLoading } = useQuery({
    queryKey: ["employees", search, page],
    queryFn: () => getEmployees({ search, page }),
  })

  const { data: departments } = useQuery({
    queryKey: ["departments"],
    queryFn: getDepartments,
  })

  const invalidateAll = () => {
    queryClient.invalidateQueries({ queryKey: ["employees"] })
    queryClient.invalidateQueries({ queryKey: ["analytics"] })
  }

  const createMutation = useMutation({
    mutationFn: createEmployee,
    onSuccess: () => { invalidateAll(); closeModal() },
  })

  const updateMutation = useMutation({
    mutationFn: (payload: any) => updateEmployee(editingId!, payload),
    onSuccess: () => { invalidateAll(); closeModal() },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteEmployee,
    onSuccess: () => invalidateAll(),
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const payload = {
      employee_id: `E${Math.floor(Math.random() * 10000)}`,
      first_name: firstName,
      last_name: lastName,
      email,
      department,
      designation,
      joining_date: new Date().toISOString().split("T")[0],
      employment_status: "ACTIVE",
      total_experience_years: parseFloat(experience),
    }
    if (editingId) updateMutation.mutate(payload)
    else createMutation.mutate(payload)
  }

  function openCreate() {
    setEditingId(null)
    setFirstName(""); setLastName(""); setEmail(""); setDepartment(""); setDesignation(""); setExperience("0")
    setIsModalOpen(true)
  }

  function openEdit(emp: Employee) {
    setEditingId(emp.id)
    setFirstName(emp.first_name)
    setLastName(emp.last_name)
    setEmail(emp.email)
    setDepartment(emp.department)
    setDesignation(emp.designation)
    setExperience(emp.total_experience_years.toString())
    setIsModalOpen(true)
  }

  function closeModal() {
    setIsModalOpen(false)
    setEditingId(null)
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Employees</h1>
          <p className="text-cyan-100 font-medium mt-1">Manage your organization's workforce.</p>
        </div>
        {isHR && (
          <button onClick={openCreate} className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-5 py-2.5 rounded-xl font-extrabold text-sm hover:from-cyan-400 hover:to-blue-500 transition-all shadow-lg shadow-cyan-500/40">
            + Add Employee
          </button>
        )}
      </header>

      <Card className="p-0 overflow-hidden">
        <div className="p-4 border-b border-white/10 bg-white/5">
          <input type="text" placeholder="Search by name, email, or role..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} className="w-full max-w-md bg-black/40 border border-white/20 rounded-xl px-4 py-2 text-sm font-semibold text-white placeholder:text-slate-400 outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/50" />
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-cyan-400 font-bold animate-pulse">Loading employees...</div>
        ) : (
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-cyan-300 uppercase bg-black/20 border-b border-white/10">
              <tr>
                <th className="px-6 py-4 font-extrabold">Name</th>
                <th className="px-6 py-4 font-extrabold">Email</th>
                <th className="px-6 py-4 font-extrabold">Role</th>
                <th className="px-6 py-4 font-extrabold">Experience</th>
                <th className="px-6 py-4 font-extrabold text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data?.results.map((emp) => (
                <tr key={emp.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  <td className="px-6 py-4 font-bold text-white">{emp.first_name} {emp.last_name}</td>
                  <td className="px-6 py-4 text-slate-300 font-medium">{emp.email}</td>
                  <td className="px-6 py-4 text-slate-300 font-medium">{emp.designation}</td>
                  <td className="px-6 py-4 text-cyan-400 font-bold">{emp.total_experience_years} yrs</td>
                  <td className="px-6 py-4 text-right space-x-3">
                    <Link to={`/employees/${emp.id}/skills`} className="text-cyan-400 hover:text-cyan-300 font-bold text-xs uppercase">Skills</Link>
                    {isHR && (
                      <>
                        <button onClick={() => openEdit(emp)} className="text-blue-400 hover:text-blue-300 font-bold text-xs uppercase">Edit</button>
                        <button onClick={() => { if(confirm("Are you sure?")) deleteMutation.mutate(emp.id) }} className="text-red-400 hover:text-red-300 font-bold text-xs uppercase">Delete</button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        <div className="p-4 border-t border-white/10 flex justify-between items-center text-sm font-bold text-white">
          <span>Total: {data?.count || 0}</span>
          <div className="space-x-2">
            <button disabled={!data?.previous} onClick={() => setPage(p => p - 1)} className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 disabled:opacity-30 transition-colors">Previous</button>
            <button disabled={!data?.next} onClick={() => setPage(p => p + 1)} className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 disabled:opacity-30 transition-colors">Next</button>
          </div>
        </div>
      </Card>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-[#0E1628] border border-white/10 rounded-2xl w-full max-w-md p-6 shadow-2xl">
            <h2 className="text-xl font-extrabold text-white mb-4">{editingId ? "Edit Employee" : "Add New Employee"}</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-extrabold text-white uppercase mb-1">First Name</label>
                  <input required value={firstName} onChange={e => setFirstName(e.target.value)} className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white" />
                </div>
                <div>
                  <label className="block text-xs font-extrabold text-white uppercase mb-1">Last Name</label>
                  <input required value={lastName} onChange={e => setLastName(e.target.value)} className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-extrabold text-white uppercase mb-1">Email</label>
                <input type="email" required value={email} onChange={e => setEmail(e.target.value)} className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white" />
              </div>
              <div>
                <label className="block text-xs font-extrabold text-white uppercase mb-1">Department</label>
                <select required value={department} onChange={e => setDepartment(e.target.value)} className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white appearance-none">
                  <option value="" disabled>Select department</option>
                  {departments?.map((d: any) => <option key={d.id} value={d.id} className="bg-[#0E1628]">{d.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-extrabold text-white uppercase mb-1">Role / Designation</label>
                <input required value={designation} onChange={e => setDesignation(e.target.value)} className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white" />
              </div>
              <div>
                <label className="block text-xs font-extrabold text-white uppercase mb-1">Total Experience (Years)</label>
                <input type="number" step="0.1" min="0" required value={experience} onChange={e => setExperience(e.target.value)} className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white" />
              </div>
              
              {(createMutation.isError || updateMutation.isError) && <div className="text-red-400 text-xs font-bold">Failed to save employee. Check console.</div>}

              <div className="flex justify-end gap-3 mt-6">
                <button type="button" onClick={closeModal} className="px-4 py-2 rounded-xl text-sm font-bold text-slate-300 hover:bg-white/10">Cancel</button>
                <button type="submit" disabled={createMutation.isPending || updateMutation.isPending} className="bg-cyan-500 hover:bg-cyan-400 text-black px-6 py-2 rounded-xl text-sm font-extrabold transition-colors">
                  {createMutation.isPending || updateMutation.isPending ? "Saving..." : "Save Employee"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}