import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Navbar from '../components/Navbar'
import Sidebar from '../components/Sidebar'
import Footer from '../components/Footer'

const AGENT_NAV = [
  { to: '/agent', label: 'Dashboard', icon: 'bi-grid-1x2', end: true },
  { to: '/agent/tickets', label: 'Assigned Tickets', icon: 'bi-ticket-detailed' },
  { to: '/agent/saved-replies', label: 'Saved Replies', icon: 'bi-chat-square-quote' },
  { to: '/agent/knowledge', label: 'Knowledge Base', icon: 'bi-book' },
  { to: '/agent/analytics', label: 'Workload & SLA', icon: 'bi-graph-up' },
  { to: '/agent/profile', label: 'Agent Profile', icon: 'bi-person' },
]

export default function AgentLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  return (
    <div className="app-container theme-agent">
      <Sidebar items={AGENT_NAV} open={sidebarOpen} onClose={() => setSidebarOpen(false)} roleLabel="Support Agent" />
      <div className="main-content">
        <Navbar onMenu={() => setSidebarOpen(true)} role="agent" />
        <main className="page-body">
          <Outlet />
        </main>
        <Footer />
      </div>
    </div>
  )
}
