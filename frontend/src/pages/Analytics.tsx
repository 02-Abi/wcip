import { useQuery } from "@tanstack/react-query"
import { getSkillsAnalytics, getDepartmentsAnalytics } from "@/api/analytics_detailed"
import { Card } from "@/components/ui/Card"

export function Analytics() {
  const { data: skillsData, isLoading: loadingSkills } = useQuery({ queryKey: ["analytics", "skills"], queryFn: () => getSkillsAnalytics() })
  const { data: deptData, isLoading: loadingDepts } = useQuery({ queryKey: ["analytics", "departments"], queryFn: getDepartmentsAnalytics })

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      <header>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Deep Analytics</h1>
        <p className="text-cyan-100 font-medium mt-1">Comprehensive breakdown of skills and department capacity.</p>
      </header>

      <section className="grid lg:grid-cols-2 gap-6">
        
        {/* Skills Breakdown */}
        <Card>
          <h2 className="text-lg font-bold mb-6 text-white">Skills Inventory by Proficiency</h2>
          {loadingSkills ? <div className="text-cyan-400 font-bold animate-pulse">Loading skills...</div> : (
            <div className="space-y-6">
              {skillsData?.by_skill.map((skill: any) => (
                <div key={skill.skill_id} className="border-b border-white/10 pb-4 last:border-0 last:pb-0">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-bold text-white">{skill.skill_name}</span>
                    <span className="text-xs font-bold text-slate-400">{skill.total} Employees</span>
                  </div>
                  <div className="flex gap-1 h-2">
                    <div className="bg-cyan-400 rounded-l" style={{ width: `${(skill.counts.BEGINNER / skill.total) * 100}%` }} title="Beginner" />
                    <div className="bg-blue-500" style={{ width: `${(skill.counts.INTERMEDIATE / skill.total) * 100}%` }} title="Intermediate" />
                    <div className="bg-violet-500" style={{ width: `${(skill.counts.ADVANCED / skill.total) * 100}%` }} title="Advanced" />
                    <div className="bg-emerald-400 rounded-r" style={{ width: `${(skill.counts.EXPERT / skill.total) * 100}%` }} title="Expert" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Department Capacity */}
        <Card>
          <h2 className="text-lg font-bold mb-6 text-white">Department Capacity Breakdown</h2>
          {loadingDepts ? <div className="text-cyan-400 font-bold animate-pulse">Loading departments...</div> : (
            <div className="space-y-4">
              {deptData?.map((dept) => (
                <div key={dept.department_id} className="flex items-center justify-between bg-white/5 p-4 rounded-xl border border-white/10">
                  <div>
                    <h3 className="font-extrabold text-white">{dept.department_name}</h3>
                    <p className="text-xs font-bold text-slate-400 mt-1">{dept.headcount} Employees</p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-extrabold text-cyan-400">{dept.avg_skills_per_employee} skills/emp</div>
                    <div className="text-xs font-bold text-slate-400 mt-1">{dept.verified_skill_pct}% Verified</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </section>
    </div>
  )
}