import { useState } from "react"
import { useParams, Link } from "react-router-dom"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { getEmployeeSkills, addEmployeeSkill, deleteEmployeeSkill } from "@/api/employeeSkills"
import { getSkills } from "@/api/skills"
import { Card } from "@/components/ui/Card"

export function EmployeeSkills() {
  const { id } = useParams()
  const queryClient = useQueryClient()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedSkill, setSelectedSkill] = useState("")
  const [proficiency, setProficiency] = useState("INTERMEDIATE")
  const [years, setYears] = useState("0")
  const [isVerified, setIsVerified] = useState(false)

  const { data: employeeSkills = [], isLoading } = useQuery({ queryKey: ["employee-skills", id], queryFn: () => getEmployeeSkills(id!) })
  const { data: skills = [] } = useQuery({ queryKey: ["skills"], queryFn: getSkills })

  const addMutation = useMutation({
    mutationFn: (payload: any) => addEmployeeSkill(id!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["employee-skills", id] })
      queryClient.invalidateQueries({ queryKey: ["analytics"] })
      setIsModalOpen(false)
      setSelectedSkill(""); setYears("0"); setIsVerified(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteEmployeeSkill,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["employee-skills", id] })
      queryClient.invalidateQueries({ queryKey: ["analytics"] })
    },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    addMutation.mutate({
      skill: selectedSkill,
      proficiency,
      years_experience: parseFloat(years),
      is_verified: isVerified,
    })
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <Link to="/employees" className="text-sm font-bold text-cyan-400 hover:text-cyan-300">← Back to Employees</Link>

      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Skills Matrix</h1>
          <p className="text-cyan-100 font-medium mt-1">Manage skills for this employee.</p>
        </div>
        <button onClick={() => setIsModalOpen(true)} className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-5 py-2.5 rounded-xl font-extrabold text-sm hover:from-cyan-400 hover:to-blue-500 transition-all shadow-lg shadow-cyan-500/40">
          + Add Skill
        </button>
      </header>

      {isLoading ? (
        <div className="text-cyan-400 font-bold animate-pulse">Loading skills...</div>
      ) : employeeSkills.length === 0 ? (
        <Card className="text-center py-12">
          <p className="text-slate-400 font-bold">No skills assigned yet. Add one to see this employee in matching results.</p>
        </Card>
      ) : (
        <Card className="p-0 overflow-hidden">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-cyan-300 uppercase bg-black/20 border-b border-white/10">
              <tr>
                <th className="px-6 py-4 font-extrabold">Skill</th>
                <th className="px-6 py-4 font-extrabold">Category</th>
                <th className="px-6 py-4 font-extrabold">Proficiency</th>
                <th className="px-6 py-4 font-extrabold">Years</th>
                <th className="px-6 py-4 font-extrabold">Verified</th>
                <th className="px-6 py-4 font-extrabold text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {employeeSkills.map((es: any) => (
                <tr key={es.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  <td className="px-6 py-4 font-bold text-white">{es.skill_name}</td>
                  <td className="px-6 py-4 text-slate-300 font-medium">{es.category_name || "—"}</td>
                  <td className="px-6 py-4">
                    <span className={`text-xs font-extrabold px-2 py-1 rounded-md ${
                      es.proficiency === 'EXPERT' ? 'bg-emerald-500/20 text-emerald-400' :
                      es.proficiency === 'ADVANCED' ? 'bg-violet-500/20 text-violet-400' :
                      es.proficiency === 'INTERMEDIATE' ? 'bg-blue-500/20 text-blue-400' :
                      'bg-cyan-500/20 text-cyan-400'
                    }`}>
                      {es.proficiency}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-cyan-400 font-bold">{es.years_experience} yrs</td>
                  <td className="px-6 py-4">
                    {es.is_verified ? <span className="text-emerald-400 font-bold text-xs">✓ Verified</span> : <span className="text-slate-500 font-bold text-xs">Unverified</span>}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button onClick={() => { if(confirm("Remove this skill?")) deleteMutation.mutate(es.id) }} className="text-red-400 hover:text-red-300 font-bold text-xs uppercase">Remove</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-[#0E1628] border border-white/10 rounded-2xl w-full max-w-md p-6 shadow-2xl">
            <h2 className="text-xl font-extrabold text-white mb-4">Add Skill to Employee</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-extrabold text-white uppercase mb-1">Skill</label>
                <select required value={selectedSkill} onChange={e => setSelectedSkill(e.target.value)} className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white appearance-none">
                  <option value="" disabled>Select skill</option>
                  {skills.map((s: any) => <option key={s.id} value={s.id} className="bg-[#0E1628]">{s.name}</option>)}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-extrabold text-white uppercase mb-1">Proficiency</label>
                  <select value={proficiency} onChange={e => setProficiency(e.target.value)} className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white appearance-none">
                    <option value="BEGINNER">Beginner</option>
                    <option value="INTERMEDIATE">Intermediate</option>
                    <option value="ADVANCED">Advanced</option>
                    <option value="EXPERT">Expert</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-extrabold text-white uppercase mb-1">Years</label>
                  <input type="number" step="0.1" min="0" required value={years} onChange={e => setYears(e.target.value)} className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white" />
                </div>
              </div>
              <div className="flex items-center gap-2 mt-2">
                <input type="checkbox" checked={isVerified} onChange={e => setIsVerified(e.target.checked)} className="w-4 h-4 accent-cyan-500" />
                <label className="text-sm font-bold text-white">Verified by Manager</label>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 rounded-xl text-sm font-bold text-slate-300 hover:bg-white/10">Cancel</button>
                <button type="submit" disabled={addMutation.isPending} className="bg-cyan-500 hover:bg-cyan-400 text-black px-6 py-2 rounded-xl text-sm font-extrabold">
                  {addMutation.isPending ? "Adding..." : "Add Skill"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}