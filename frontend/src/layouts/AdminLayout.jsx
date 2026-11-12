import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Navbar from '../components/Navbar'
import Sidebar from '../components/Sidebar'
import Footer from '../components/Footer'

const ADMIN_NAV = [
  { to: '/admin', label: 'Dashboard', icon: 'bi-grid-1x2', end: true },
  { to: '/admin/tickets', label: 'Tickets', icon: 'bi-ticket-detailed' },
  { to: '/admin/users', label: 'User Directory', icon: 'bi-people' },
  { to: '/admin/agents', label: 'Agent Management', icon: 'bi-person-badge' },
  { to: '/admin/categories', label: 'Categories', icon: 'bi-tags' },
  { to: '/admin/knowledge', label: 'Knowledge Base', icon: 'bi-book' },
  { to: '/admin/analytics', label: 'Analytics', icon: 'bi-graph-up' },
  { to: '/admin/reports', label: 'Reports & Export', icon: 'bi-file-earmark-text' },
  { to: '/admin/sla', label: 'SLA Monitoring', icon: 'bi-shield-check' },
  { to: '/admin/audit', label: 'Audit Logs', icon: 'bi-clock-history' },
  { to: '/admin/settings', label: 'Settings', icon: 'bi-gear' },
]

export default function AdminLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  return (
    <div className="app-container theme-admin">
      <Sidebar items={ADMIN_NAV} open={sidebarOpen} onClose={() => setSidebarOpen(false)} roleLabel="Administrator" />
      <div className="main-content">
        <Navbar onMenu={() => setSidebarOpen(true)} role="admin" />
        <main className="page-body">
          <Outlet />
        </main>
        <Footer />
      </div>
    </div>
  )
}
