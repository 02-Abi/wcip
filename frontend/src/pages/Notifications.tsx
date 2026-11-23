import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { getNotifications, markNotificationRead, markAllNotificationsRead } from "@/api/notifications"
import { Card } from "@/components/ui/Card"

export function Notifications() {
  const queryClient = useQueryClient()
  
  const { data: notifications = [], isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: getNotifications,
  })

  const readMutation = useMutation({
    mutationFn: markNotificationRead,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  })

  const readAllMutation = useMutation({
    mutationFn: markAllNotificationsRead,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  })

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Notifications</h1>
          <p className="text-cyan-100 font-medium mt-1">Your alerts and system messages.</p>
        </div>
        <button 
          onClick={() => readAllMutation.mutate()} 
          disabled={readAllMutation.isPending}
          className="text-sm font-bold text-cyan-400 hover:text-cyan-300"
        >
          Mark all as read
        </button>
      </header>

      {isLoading ? (
        <div className="text-cyan-400 font-bold animate-pulse">Loading inbox...</div>
      ) : notifications.length === 0 ? (
        <Card className="text-center py-12">
          <p className="text-slate-400 font-bold">Your inbox is empty.</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {notifications.map((n: any) => (
            <Card 
              key={n.id} 
              className={`p-5 flex gap-4 transition-colors ${n.is_read ? 'opacity-60' : 'border-l-4 border-l-cyan-500'}`}
            >
              <div className="flex-1">
                <div className="flex justify-between items-start">
                  <h3 className={`font-extrabold ${n.is_read ? 'text-slate-300' : 'text-white'}`}>{n.title}</h3>
                  <span className="text-xs font-bold text-slate-400">{new Date(n.created_at).toLocaleDateString()}</span>
                </div>
                <p className="text-sm text-slate-300 mt-1">{n.body}</p>
              </div>
              {!n.is_read && (
                <button 
                  onClick={() => readMutation.mutate(n.id)}
                  className="text-xs font-bold text-cyan-400 hover:text-cyan-300 shrink-0 self-center"
                >
                  Mark read
                </button>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}