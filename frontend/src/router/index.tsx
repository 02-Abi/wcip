import { createBrowserRouter, Navigate } from "react-router-dom"
import { RequireAuth } from "@/features/auth/RequireAuth"
import { LoginPage } from "@/features/auth/LoginPage"
import { SignupPage } from "@/features/auth/SignupPage"
import { AppShell } from "@/layouts/AppShell"
import { Dashboard } from "@/pages/Dashboard"
import { Employees } from "@/pages/Employees"
import { Projects } from "@/pages/Projects"
import { ProjectMatches } from "@/pages/ProjectMatches"
import { Skills } from "@/pages/Skills"
import { Analytics } from "@/pages/Analytics" // <-- Import
import { Notifications } from "@/pages/Notifications" // <-- Import

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  { path: "/signup", element: <SignupPage /> },
  {
    element: <RequireAuth />,
    children: [
      {
        element: <AppShell />,
        children: [
          { index: true, element: <Dashboard /> },
          { path: "employees", element: <Employees /> },
          { path: "projects", element: <Projects /> },
          { path: "projects/:id/matches", element: <ProjectMatches /> },
          { path: "skills", element: <Skills /> },
          { path: "analytics", element: <Analytics /> }, // <-- Connect
          { path: "notifications", element: <Notifications /> }, // <-- Connect
        ],
      },
    ],
  },
  { path: "*", element: <Navigate to="/login" replace /> },
])