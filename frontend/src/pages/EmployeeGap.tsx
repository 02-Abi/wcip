import { useParams, Link, useSearchParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { getEmployeeGap, getEmployeeRecommendations } from "@/api/intelligence"
import { Card } from "@/components/ui/Card"

export function EmployeeGap() {
  const { id } = useParams()
  const [searchParams] = useSearchParams()
  const projectId = searchParams.get("project")

  const { data: gap, isLoading: loadingGap } = useQuery({
    queryKey: ["gap", id, projectId],
    queryFn: () => getEmployeeGap(id!, projectId!),
    enabled: !!projectId,
  })

  const { data: recommendations = [], isLoading: loadingRecs } = useQuery({
    queryKey: ["recommendations", id, projectId],
    queryFn: () => getEmployeeRecommendations(id!, projectId!),
    enabled: !!projectId,
  })

  if (!projectId) {
    return <div className="text-red-400 font-bold text-center mt-10">No project selected. Go back to the project matches and click a gap report.</div>
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <Link to={`/projects/${projectId}/matches`} className="text-sm font-bold text-cyan-400 hover:text-cyan-300">← Back to Matches</Link>

      <header>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Skill Gap & Learning Plan</h1>
        <p className="text-cyan-100 font-medium mt-1">Detailed analysis for this employee against the project requirements.</p>
      </header>

      {loadingGap || loadingRecs ? (
        <div className="text-cyan-400 font-bold animate-pulse">Analyzing intelligence...</div>
      ) : (
        <div className="grid lg:grid-cols-3 gap-6">
          
          {/* LEFT: Gap Analysis */}
          <div className="space-y-4 lg:col-span-2">
            <Card className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-bold text-white">Coverage Score</h2>
                <div className={`text-4xl font-extrabold ${gap?.fully_qualified ? 'text-emerald-400' : 'text-yellow-400'}`}>
                  {gap?.coverage_pct}%
                </div>
              </div>
              <div className="h-3 bg-white/10 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${gap?.fully_qualified ? 'bg-emerald-400' : 'bg-gradient-to-r from-yellow-400 to-orange-500'}`} style={{ width: `${gap?.coverage_pct}%` }} />
              </div>
            </Card>

            <Card>
              <h2 className="text-lg font-bold mb-4 text-red-400">Mandatory Gaps</h2>
              {gap?.mandatory_gaps.length === 0 ? (
                <p className="text-sm font-bold text-emerald-400">✓ No mandatory gaps! Employee is fully qualified.</p>
              ) : (
                <div className="space-y-3">
                  {gap?.mandatory_gaps.map((g: any, i: number) => (
                    <div key={i} className="flex justify-between items-center bg-red-500/10 border border-red-500/20 p-3 rounded-lg">
                      <div>
                        <span className="font-bold text-white">{g.skill_name}</span>
                        <span className="text-xs font-bold text-slate-400 ml-2">Requires {g.required_proficiency}, {g.required_years} yrs</span>
                      </div>
                      <span className="text-xs font-extrabold text-red-300 uppercase">{g.status.replace("_", " ")}</span>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>

          {/* RIGHT: Learning Plan */}
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-white">Learning Plan</h2>
            {recommendations.length === 0 ? (
              <Card className="text-center py-8">
                <p className="text-slate-400 font-bold">No recommendations needed.</p>
              </Card>
            ) : (
              recommendations.map((rec: any) => (
                <Card key={rec.rank} className="p-4 relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-1 h-full bg-cyan-400" />
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-extrabold text-white">{rec.skill_name}</h3>
                    <span className="text-[10px] font-extrabold text-cyan-400 bg-cyan-500/10 px-2 py-1 rounded-md uppercase">Priority {rec.rank}</span>
                  </div>
                  <p className="text-xs text-slate-300 font-medium mb-3">{rec.reason}</p>
                  <div className="flex justify-between items-center text-xs font-bold border-t border-white/10 pt-2">
                    <span className="text-slate-400">{rec.action_type.replace("_", " ")}</span>
                    <span className="text-cyan-400">{rec.estimated_effort_hours} hrs</span>
                  </div>
                </Card>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}