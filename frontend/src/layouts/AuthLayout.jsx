import { Outlet } from 'react-router-dom'
import BrandLogo from '../components/BrandLogo'

export default function AuthLayout() {
  return (
    <div className="d-flex flex-column min-vh-100 justify-content-center align-items-center bg-light p-3">
      <div className="w-100" style={{ maxWidth: '440px' }}>
        <div className="text-center mb-4">
          <div className="mb-2">
            <BrandLogo size={52} />
          </div>
          <h2 className="fw-bold h4 mb-1">Helpdesk AI</h2>
          <p className="text-muted small">Intelligent Customer Support &amp; Helpdesk Platform</p>
        </div>
        <div className="card shadow-sm border-0">
          <div className="card-body p-4">
            <Outlet />
          </div>
        </div>
      </div>
    </div>
  )
}
