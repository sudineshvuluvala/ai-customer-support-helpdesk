import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth, homeFor } from '../context/AuthContext'

// Layouts
import AuthLayout from '../layouts/AuthLayout'
import AdminLayout from '../layouts/AdminLayout'
import AgentLayout from '../layouts/AgentLayout'
import CustomerLayout from '../layouts/CustomerLayout'

// Protected Route Guards
import ProtectedRoute from './ProtectedRoute'
import RoleBasedRoute from './RoleBasedRoute'

// Pages
import LoginPage from '../pages/auth/LoginPage'
import RegisterPage from '../pages/auth/RegisterPage'
import ForgotPasswordPage from '../pages/auth/ForgotPasswordPage'
import ResetPasswordPage from '../pages/auth/ResetPasswordPage'
import UnauthorizedPage from '../pages/shared/UnauthorizedPage'
import NotFoundPage from '../pages/shared/NotFoundPage'

// Admin Pages
import AdminDashboardPage from '../pages/admin/AdminDashboardPage'
import UserManagementPage from '../pages/admin/UserManagementPage'
import CategoryManagementPage from '../pages/admin/CategoryManagementPage'
import KnowledgeAdminPage from '../pages/admin/KnowledgeAdminPage'
import AnalyticsPage from '../pages/admin/AnalyticsPage'
import ReportsPage from '../pages/admin/ReportsPage'
import SlaMonitoringPage from '../pages/admin/SlaMonitoringPage'
import AuditLogsPage from '../pages/admin/AuditLogsPage'
import SettingsPage from '../pages/admin/SettingsPage'

// Agent Pages
import AgentDashboardPage from '../pages/agent/AgentDashboardPage'
import SavedRepliesPage from '../pages/agent/SavedRepliesPage'

// Customer Pages
import CustomerDashboardPage from '../pages/customer/CustomerDashboardPage'
import CreateTicketPage from '../pages/customer/CreateTicketPage'
import AiAssistantPage from '../pages/customer/AiAssistantPage'

// Shared Pages
import TicketListPage from '../pages/shared/TicketListPage'
import TicketDetailPage from '../pages/shared/TicketDetailPage'
import KnowledgeBasePage from '../pages/shared/KnowledgeBasePage'
import ProfilePage from '../pages/shared/ProfilePage'
import NotificationsPage from '../pages/shared/NotificationsPage'

export default function AppRoutes() {
  const { user } = useAuth()

  return (
    <Routes>
      {/* Root redirect */}
      <Route path="/" element={<Navigate to={user ? homeFor(user.role) : '/login'} replace />} />

      {/* Public Auth Routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={user ? <Navigate to={homeFor(user.role)} replace /> : <LoginPage />} />
        <Route path="/register" element={user ? <Navigate to={homeFor(user.role)} replace /> : <RegisterPage />} />
        <Route path="/forgot-password" element={user ? <Navigate to={homeFor(user.role)} replace /> : <ForgotPasswordPage />} />
        <Route path="/reset-password" element={user ? <Navigate to={homeFor(user.role)} replace /> : <ResetPasswordPage />} />
      </Route>

      {/* Authenticated Root Guard */}
      <Route element={<ProtectedRoute />}>
        {/* Admin Portal */}
        <Route element={<RoleBasedRoute allowedRoles={['admin']} />}>
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<AdminDashboardPage />} />
            <Route path="tickets" element={<TicketListPage role="admin" />} />
            <Route path="tickets/:id" element={<TicketDetailPage role="admin" />} />
            <Route path="users" element={<UserManagementPage />} />
            <Route path="agents" element={<UserManagementPage />} />
            <Route path="categories" element={<CategoryManagementPage />} />
            <Route path="knowledge" element={<KnowledgeAdminPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="sla" element={<SlaMonitoringPage />} />
            <Route path="audit" element={<AuditLogsPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="notifications" element={<NotificationsPage />} />
          </Route>
        </Route>

        {/* Support Agent Portal */}
        <Route element={<RoleBasedRoute allowedRoles={['agent']} />}>
          <Route path="/agent" element={<AgentLayout />}>
            <Route index element={<AgentDashboardPage />} />
            <Route path="tickets" element={<TicketListPage role="agent" />} />
            <Route path="tickets/:id" element={<TicketDetailPage role="agent" />} />
            <Route path="saved-replies" element={<SavedRepliesPage />} />
            <Route path="knowledge" element={<KnowledgeBasePage role="agent" />} />
            <Route path="knowledge/:id" element={<KnowledgeBasePage role="agent" />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="notifications" element={<NotificationsPage />} />
          </Route>
        </Route>

        {/* Customer Portal */}
        <Route element={<RoleBasedRoute allowedRoles={['customer']} />}>
          <Route path="/customer" element={<CustomerLayout />}>
            <Route index element={<CustomerDashboardPage />} />
            <Route path="tickets/create" element={<CreateTicketPage />} />
            <Route path="tickets" element={<TicketListPage role="customer" />} />
            <Route path="tickets/:id" element={<TicketDetailPage role="customer" />} />
            <Route path="assistant" element={<AiAssistantPage />} />
            <Route path="knowledge" element={<KnowledgeBasePage role="customer" />} />
            <Route path="knowledge/:id" element={<KnowledgeBasePage role="customer" />} />
            <Route path="notifications" element={<NotificationsPage />} />
            <Route path="profile" element={<ProfilePage />} />
          </Route>
        </Route>
      </Route>

      {/* Exception & Error Routes */}
      <Route path="/unauthorized" element={<UnauthorizedPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
