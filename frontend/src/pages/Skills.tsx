import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  getSkillCategories,
  createSkillCategory,
  getSkills,
  createSkill,
  type SkillCategory,
  type Skill,
} from "@/api/skills"
import { Card } from "@/components/ui/Card"

export function Skills() {
  const queryClient = useQueryClient()
  const [isCatModalOpen, setIsCatModalOpen] = useState(false)
  const [isSkillModalOpen, setIsSkillModalOpen] = useState(false)

  const [catName, setCatName] = useState("")
  const [catDesc, setCatDesc] = useState("")

  const [skillName, setSkillName] = useState("")
  const [skillCat, setSkillCat] = useState("")
  const [skillDesc, setSkillDesc] = useState("")

  const { data: categories = [] } = useQuery({
    queryKey: ["skill-categories"],
    queryFn: getSkillCategories,
  })
  const { data: skills = [] } = useQuery({
    queryKey: ["skills"],
    queryFn: getSkills,
  })

  const catMutation = useMutation({
    mutationFn: createSkillCategory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["skill-categories"] })
      setIsCatModalOpen(false)
      setCatName("")
      setCatDesc("")
    },
  })

  const skillMutation = useMutation({
    mutationFn: createSkill,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["skills"] })
      queryClient.invalidateQueries({ queryKey: ["analytics"] })
      setIsSkillModalOpen(false)
      setSkillName("")
      setSkillCat("")
      setSkillDesc("")
    },
  })

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <header>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Skills Taxonomy</h1>
        <p className="text-cyan-100 font-medium mt-1">
          Manage the skills your organization tracks.
        </p>
      </header>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Categories Column */}
        <div className="space-y-4">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-lg font-bold text-white">Categories</h2>
            <button
              onClick={() => setIsCatModalOpen(true)}
              className="text-xs font-bold text-cyan-400 hover:text-cyan-300"
            >
              + Add Category
            </button>
          </div>
          {categories.map((cat: SkillCategory) => (
            <Card key={cat.id} className="p-4">
              <h3 className="font-extrabold text-white">{cat.name}</h3>
              <p className="text-xs text-slate-300 mt-1">
                {cat.description || "No description."}
              </p>
            </Card>
          ))}
        </div>

        {/* Skills Column */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-lg font-bold text-white">Skills</h2>
            <button
              onClick={() => setIsSkillModalOpen(true)}
              className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-4 py-2 rounded-xl font-extrabold text-xs hover:from-cyan-400 hover:to-blue-500 transition-all shadow-lg shadow-cyan-500/40"
            >
              + Add Skill
            </button>
          </div>
          <Card className="p-0 overflow-hidden">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-cyan-300 uppercase bg-black/20 border-b border-white/10">
                <tr>
                  <th className="px-6 py-4 font-extrabold">Skill Name</th>
                  <th className="px-6 py-4 font-extrabold">Category</th>
                </tr>
              </thead>
              <tbody>
                {skills.map((skill: Skill) => (
                  <tr
                    key={skill.id}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors"
                  >
                    <td className="px-6 py-4 font-bold text-white">{skill.name}</td>
                    <td className="px-6 py-4 text-slate-300 font-medium">
                      {skill.category_name || "Uncategorized"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      </div>

      {/* Add Category Modal */}
      {isCatModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-[#0E1628] border border-white/10 rounded-2xl w-full max-w-md p-6 shadow-2xl">
            <h2 className="text-xl font-extrabold text-white mb-4">Add Category</h2>
            <form
              onSubmit={(e) => {
                e.preventDefault()
                catMutation.mutate({ name: catName, description: catDesc })
              }}
              className="space-y-4"
            >
              <div>
                <label className="block text-xs font-extrabold text-white uppercase mb-1">
                  Name
                </label>
                <input
                  required
                  value={catName}
                  onChange={(e) => setCatName(e.target.value)}
                  className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white"
                />
              </div>
              <div>
                <label className="block text-xs font-extrabold text-white uppercase mb-1">
                  Description
                </label>
                <input
                  value={catDesc}
                  onChange={(e) => setCatDesc(e.target.value)}
                  className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white"
                />
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setIsCatModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-sm font-bold text-slate-300 hover:bg-white/10"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={catMutation.isPending}
                  className="bg-cyan-500 hover:bg-cyan-400 text-black px-6 py-2 rounded-xl text-sm font-extrabold"
                >
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Skill Modal */}
      {isSkillModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-[#0E1628] border border-white/10 rounded-2xl w-full max-w-md p-6 shadow-2xl">
            <h2 className="text-xl font-extrabold text-white mb-4">Add Skill</h2>
            <form
              onSubmit={(e) => {
                e.preventDefault()
                skillMutation.mutate({
                  name: skillName,
                  category: skillCat,
                  description: skillDesc,
                })
              }}
              className="space-y-4"
            >
              <div>
                <label className="block text-xs font-extrabold text-white uppercase mb-1">
                  Name
                </label>
                <input
                  required
                  value={skillName}
                  onChange={(e) => setSkillName(e.target.value)}
                  className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white"
                />
              </div>
              <div>
                <label className="block text-xs font-extrabold text-white uppercase mb-1">
                  Category
                </label>
                <select
                  required
                  value={skillCat}
                  onChange={(e) => setSkillCat(e.target.value)}
                  className="w-full bg-black/40 border border-white/20 rounded-lg px-3 py-2 text-white appearance-none"
                >
                  <option value="" disabled>
                    Select category
                  </option>
                  {categories.map((c: SkillCategory) => (
                    <option key={c.id} value={c.id} className="bg-[#0E1628]">
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setIsSkillModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-sm font-bold text-slate-300 hover:bg-white/10"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={skillMutation.isPending}
                  className="bg-cyan-500 hover:bg-cyan-400 text-black px-6 py-2 rounded-xl text-sm font-extrabold"
                >
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}