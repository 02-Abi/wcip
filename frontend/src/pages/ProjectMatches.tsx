import { useState } from "react"
import { useParams, Link } from "react-router-dom"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { getProject, getRequiredSkills, addRequiredSkill, getProjectMatches, getSkills, deleteRequiredSkill } from "@/api/projects"
import { Card } from "@/components/ui/Card"

export function ProjectMatches() {
  const { id } = useParams()
  const queryClient = useQueryClient()
  
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedSkill, setSelectedSkill] = useState("")
  const [proficiency, setProficiency] = useState("INTERMEDIATE")
  const [years, setYears] = useState("0")
  const [isMandatory, setIsMandatory] = useState(true)

  // Default to empty arrays to prevent map crashes
  const { data: project } = useQuery({ queryKey: ["project", id], queryFn: () => getProject(id!) })
  const { data: requirements = [] } = useQuery({ queryKey: ["requirements", id], queryFn: () => getRequiredSkills(id!) })
  const { data: skills = [] } = useQuery({ queryKey: ["skills"], queryFn: getSkills })
  const { data: matches = [], isLoading: loadingMatches } = useQuery({ 
    queryKey: ["matches", id], 
    queryFn: () => getProjectMatches(id!) 
  })

  const addMutation = useMutation({
    mutationFn: (payload: any) => addRequiredSkill(id!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["requirements", id] })
      queryClient.invalidateQueries({ queryKey: ["matches", id] })
      setIsModalOpen(false)
      setSelectedSkill(""); setYears("0")
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteRequiredSkill,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["requirements", id] })
      queryClient.invalidateQueries({ queryKey: ["matches", id] })
    },
  })

  function handleAddSkill(e: React.FormEvent) {
    e.preventDefault()
    addMutation.mutate({
      skill: selectedSkill,
      minimum_proficiency: proficiency,
      minimum_years: parseFloat(years),
      is_mandatory: isMandatory,
      weight: 1.0,
    })
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <Link to="/projects" className="text-sm font-bold text-cyan-400 hover:text-cyan-300">← Back to Projects</Link>
      
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">{project?.name || "Loading..."}</h1>
          <p className="text-cyan-100 font-medium mt-1">Manage required skills and view employee matches.</p>
        </div>
        <button onClick={() => setIsModalOpen(true)} className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-5 py-2.5 rounded-xl font-extrabold text-sm hover:from-cyan-400 hover:to-blue-500 transition-all shadow-lg shadow-cyan-500/40">
          + Add Required Skill
        </button>
      </header>

      <div className="grid lg:grid-cols-3 gap-6">
        
        {/* LEFT: Required Skills */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-white mb-2">Required Skills</h2>
          {requirements.length === 0 ? (
            <Card className="p-4 text-sm font-bold text-slate-400 text-center">No skills required yet. Add one!</Card>
          ) : (
            requirements.map((req: any) => (
              <Card key={req.id} className="p-4 relative group">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-extrabold text-white">{req.skill_name}</h3>
                  <button onClick={() => deleteMutation.mutate(req.id)} className="text-red-400 opacity-0 group-hover:opacity-100 transition-opacity text-xs font-bold">✕</button>
                </div>
                <p className="text-xs text-slate-300 font-medium">Min level: <span className="text-cyan-400">{req.minimum_proficiency}</span></p>
                <p className="text-xs text-slate-300 font-medium">Min years: <span className="text-cyan-400">{req.minimum_years}</span></p>
              </Card>
            ))
          )}
        </div>

        {/* RIGHT: Matches */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-bold text-white mb-2">Ranked Matches</h2>
          {loadingMatches ? (
            <div className="text-cyan-400 font-bold animate-pulse">Calculating matches...</div>
          ) : matches.length === 0 ? (
            <Card className="p-4 text-sm font-bold text-slate-400 text-center">No matches yet. Add required skills to see rankings.</Card>
          ) : (
            matches.map((match: any, i: number) => (
              <Card key={match.employee_id} className="p-5 flex items-center gap-4 hover:bg-white/10 transition-colors">
                <div className="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 font-extrabold text-lg shrink-0">
                  #{i + 1}
                </div>
                <div className="flex-1">
                  <h3 className="font-extrabold text-white text-lg">{match.employee_name}</h3>
                  <p className="text-sm text-slate-300 font-medium mt-1">{match.explanation}</p>
                </div>
                <div className="text-right shrink-0">
                  <div className={`text-2xl font-extrabold ${match.score > 80 ? 'text-emerald-400' : match.score > 50 ? 'text-yellow-400' : 'text-red-400'}`}>
                    {match.score}%
                  </div>
                  <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Match</div>
                </div>
              </Card>
            ))
          )}
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-[#0E1628] border border-white/10 rounded-2xl w-full max-w-md p-6 shadow-2xl">
            <h2 className="text-xl font-extrabold text-white mb-4">Add Required Skill</h2>
            <form onSubmit={handleAddSkill} className="space-y-4">
              <div>
                <label className="block text-xs font-extrabold text-white uppercase mb-1">Skill</label>
                <select required value={selectedSkill} onChange={e => setSelectedSkill(e.target.value)} className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white appearance-none">
                  <option value="" disabled>Select a skill</option>
                  {skills.map((s: any) => <option key={s.id} value={s.id} className="bg-[#0E1628]">{s.name}</option>)}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-extrabold text-white uppercase mb-1">Min Proficiency</label>
                  <select value={proficiency} onChange={e => setProficiency(e.target.value)} className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white appearance-none">
                    <option value="BEGINNER">Beginner</option>
                    <option value="INTERMEDIATE">Intermediate</option>
                    <option value="ADVANCED">Advanced</option>
                    <option value="EXPERT">Expert</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-extrabold text-white uppercase mb-1">Min Years</label>
                  <input type="number" step="0.1" min="0" required value={years} onChange={e => setYears(e.target.value)} className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white" />
                </div>
              </div>
              <div className="flex items-center gap-2 mt-2">
                <input type="checkbox" checked={isMandatory} onChange={e => setIsMandatory(e.target.checked)} className="w-4 h-4 accent-cyan-500" />
                <label className="text-sm font-bold text-white">Is Mandatory?</label>
              </div>
              
              {addMutation.isError && <div className="text-red-400 text-xs font-bold">Failed to add skill.</div>}
              
              <div className="flex justify-end gap-3 mt-6">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 rounded-xl text-sm font-bold text-slate-300 hover:bg-white/10">Cancel</button>
                <button type="submit" disabled={addMutation.isPending} className="bg-cyan-500 hover:bg-cyan-400 text-black px-6 py-2 rounded-xl text-sm font-extrabold transition-colors">
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