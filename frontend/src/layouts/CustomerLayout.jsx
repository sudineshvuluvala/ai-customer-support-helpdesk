import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Navbar from '../components/Navbar'
import Sidebar from '../components/Sidebar'
import Footer from '../components/Footer'

const CUSTOMER_NAV = [
  { to: '/customer', label: 'Dashboard', icon: 'bi-grid-1x2', end: true },
  { to: '/customer/tickets/create', label: 'Create Ticket', icon: 'bi-plus-circle' },
  { to: '/customer/tickets', label: 'My Tickets', icon: 'bi-ticket-detailed' },
  { to: '/customer/assistant', label: 'AI Assistant', icon: 'bi-robot' },
  { to: '/customer/knowledge', label: 'Knowledge Base', icon: 'bi-book' },
  { to: '/customer/notifications', label: 'Notifications', icon: 'bi-bell' },
  { to: '/customer/profile', label: 'My Profile', icon: 'bi-person' },
]

export default function CustomerLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  return (
    <div className="app-container theme-customer">
      <Sidebar items={CUSTOMER_NAV} open={sidebarOpen} onClose={() => setSidebarOpen(false)} roleLabel="Customer" />
      <div className="main-content">
        <Navbar onMenu={() => setSidebarOpen(true)} role="customer" />
        <main className="page-body">
          <Outlet />
        </main>
        <Footer />
      </div>
    </div>
  )
}
