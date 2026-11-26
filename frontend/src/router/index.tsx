import { createBrowserRouter, Navigate } from "react-router-dom"
import { RequireAuth } from "@/features/auth/RequireAuth"
import { LoginPage } from "@/features/auth/LoginPage"
import { SignupPage } from "@/features/auth/SignupPage"
import { AppShell } from "@/layouts/AppShell"
import { Dashboard } from "@/pages/Dashboard"
import { Employees } from "@/pages/Employees"
import { EmployeeSkills } from "@/pages/EmployeeSkills"
import { EmployeeGap } from "@/pages/EmployeeGap"
import { Projects } from "@/pages/Projects"
import { ProjectMatches } from "@/pages/ProjectMatches"
import { Skills } from "@/pages/Skills"
import { Analytics } from "@/pages/Analytics"
import { Notifications } from "@/pages/Notifications"

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
          { path: "employees/:id/skills", element: <EmployeeSkills /> },
          { path: "employees/:id/gap", element: <EmployeeGap /> },
          { path: "projects", element: <Projects /> },
          { path: "projects/:id/matches", element: <ProjectMatches /> },
          { path: "skills", element: <Skills /> },
          { path: "analytics", element: <Analytics /> },
          { path: "notifications", element: <Notifications /> },
        ],
      },
    ],
  },
  { path: "*", element: <Navigate to="/login" replace /> },
])