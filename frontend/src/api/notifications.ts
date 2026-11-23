import { api } from "./client"

export type Notification = {
  id: string
  kind: string
  title: string
  body: string
  is_read: boolean
  created_at: string
}

export async function getNotifications() {
  const { data } = await api.get<any>("/notifications/")
  return data.results ? data.results : data
}

export async function markNotificationRead(id: string) {
  await api.post(`/notifications/${id}/read/`)
}

export async function markAllNotificationsRead() {
  await api.post("/notifications/read-all/")
}