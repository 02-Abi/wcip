import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Link } from "react-router-dom"
import { getProjects, createProject, type Project } from "@/api/projects"
import { Card } from "@/components/ui/Card"

export function Projects() {
  const queryClient = useQueryClient()
  const [isModalOpen, setIsModalOpen] = useState(false)

  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [priority, setPriority] = useState("MEDIUM")
  const [headcount, setHeadcount] = useState("1")

  const { data = [], isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: getProjects,
  })

  const mutation = useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] })
      queryClient.invalidateQueries({ queryKey: ["analytics"] })
      setIsModalOpen(false)
      setName("")
      setDescription("")
      setPriority("MEDIUM")
      setHeadcount("1")
    },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    mutation.mutate({
      name,
      description,
      priority,
      status: "ACTIVE",
      headcount_needed: parseInt(headcount),
    })
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Projects</h1>
          <p className="text-cyan-100 font-medium mt-1">
            Manage delivery projects and find the right people.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-5 py-2.5 rounded-xl font-extrabold text-sm hover:from-cyan-400 hover:to-blue-500 transition-all shadow-lg shadow-cyan-500/40"
        >
          + Create Project
        </button>
      </header>

      {isLoading ? (
        <div className="text-cyan-400 font-bold animate-pulse">Loading projects...</div>
      ) : data.length === 0 ? (
        <div className="text-slate-400 font-bold text-center py-10">
          No projects found. Create one to get started.
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.map((proj: Project) => (
            <Card key={proj.id} className="flex flex-col h-full relative group">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-extrabold text-white">{proj.name}</h3>
                <span
                  className={`text-[10px] font-extrabold px-2 py-1 rounded-md uppercase tracking-wider ${
                    proj.priority === "CRITICAL"
                      ? "bg-red-500/20 text-red-400"
                      : "bg-blue-500/20 text-blue-400"
                  }`}
                >
                  {proj.priority}
                </span>
              </div>
              <p className="text-sm text-slate-300 font-medium mb-6 flex-1">
                {proj.description || "No description provided."}
              </p>

              <div className="flex justify-between items-center mt-auto border-t border-white/10 pt-4">
                <span className="text-xs font-bold text-slate-400">
                  Needs {proj.headcount_needed} people
                </span>
                <Link
                  to={`/projects/${proj.id}/matches`}
                  className="text-xs font-extrabold text-cyan-400 hover:text-cyan-300 bg-cyan-500/10 px-3 py-1.5 rounded-lg transition-colors"
                >
                  View Matches →
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-[#0E1628] border border-white/10 rounded-2xl w-full max-w-md p-6 shadow-2xl">
            <h2 className="text-xl font-extrabold text-white mb-4">Create New Project</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-extrabold text-white uppercase mb-1">
                  Project Name
                </label>
                <input
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white"
                />
              </div>
              <div>
                <label className="block text-xs font-extrabold text-white uppercase mb-1">
                  Description
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white h-20"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-extrabold text-white uppercase mb-1">
                    Priority
                  </label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white appearance-none"
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="CRITICAL">Critical</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-extrabold text-white uppercase mb-1">
                    Headcount Needed
                  </label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={headcount}
                    onChange={(e) => setHeadcount(e.target.value)}
                    className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white"
                  />
                </div>
              </div>

              {mutation.isError && (
                <div className="text-red-400 text-xs font-bold">Failed to create project.</div>
              )}
              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-sm font-bold text-slate-300 hover:bg-white/10"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={mutation.isPending}
                  className="bg-cyan-500 hover:bg-cyan-400 text-black px-6 py-2 rounded-xl text-sm font-extrabold transition-colors"
                >
                  {mutation.isPending ? "Creating..." : "Create Project"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}