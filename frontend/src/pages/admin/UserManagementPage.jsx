import { useState } from 'react'
import { userService } from '../../services/userService'
import { useFetch, useDebounce } from '../../hooks/useFetch'
import DataTable from '../../components/DataTable'
import SearchBar from '../../components/SearchBar'
import Pagination from '../../components/Pagination'
import Modal from '../../components/Modal'
import ErrorMessage from '../../components/ErrorMessage'
import UserAvatar from '../../components/UserAvatar'
import { fmtDate } from '../../utils/format'

export default function UserManagementPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const debouncedSearch = useDebounce(search, 300)

  const { data, loading, error, reload } = useFetch(
    () => userService.adminUsers({ page, per_page: 10, q: debouncedSearch || undefined, role: roleFilter || undefined }),
    [page, debouncedSearch, roleFilter]
  )

  // Edit / Status toggle state
  const [editUser, setEditUser] = useState(null)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [role, setRole] = useState('customer')

  // Create User Modal
  const [createModal, setCreateModal] = useState(false)
  const [cName, setCName] = useState('')
  const [cEmail, setCEmail] = useState('')
  const [cPassword, setCPassword] = useState('')
  const [cRole, setCRole] = useState('agent')
  const [createErr, setCreateErr] = useState(null)

  const handleToggleStatus = async (user) => {
    const nextStatus = user.account_status === 'active' ? 'inactive' : 'active'
    if (!confirm(`Are you sure you want to mark ${user.email} as ${nextStatus}?`)) return
    try {
      await userService.setStatus(user.user_id, nextStatus)
      reload()
    } catch (ex) {
      alert(ex.message || 'Failed to update user status')
    }
  }

  const handleSaveEdit = async () => {
    try {
      await userService.updateUser(editUser.user_id, { name, email, role })
      setEditUser(null)
      reload()
    } catch (ex) {
      alert(ex.message || 'Update failed')
    }
  }

  const handleCreateUser = async (e) => {
    e.preventDefault()
    setCreateErr(null)
    try {
      await userService.createUser({ name: cName, email: cEmail, password: cPassword, role: cRole })
      setCreateModal(false)
      setCName(''); setCEmail(''); setCPassword(''); setCRole('agent')
      reload()
    } catch (ex) {
      setCreateErr(ex)
    }
  }

  const columns = [
    {
      key: 'name',
      label: 'User',
      render: (u) => (
        <div className="d-flex align-items-center gap-2">
          <UserAvatar user={u} size={28} />
          <span className="fw-semibold">{u.name.replace(' [SEED]', '')}</span>
        </div>
      ),
    },
    { key: 'email', label: 'Email Address' },
    {
      key: 'role',
      label: 'Role',
      render: (u) => (
        <span className={`badge text-capitalize text-bg-${u.role === 'admin' ? 'danger' : u.role === 'agent' ? 'primary' : 'success'}`}>
          {u.role}
        </span>
      ),
    },
    {
      key: 'account_status',
      label: 'Status',
      render: (u) => (
        <span className={`badge text-bg-${u.account_status === 'active' ? 'success' : 'secondary'}`}>
          {u.account_status}
        </span>
      ),
    },
    { key: 'created_at', label: 'Joined', render: (u) => <span className="small text-muted">{fmtDate(u.created_at)}</span> },
    {
      key: 'actions',
      label: 'Actions',
      render: (u) => (
        <div className="btn-group btn-group-sm">
          <button
            className="btn btn-outline-secondary"
            onClick={() => {
              setEditUser(u)
              setName(u.name.replace(' [SEED]', ''))
              setEmail(u.email)
              setRole(u.role)
            }}
          >
            Edit
          </button>
          <button
            className={`btn btn-outline-${u.account_status === 'active' ? 'warning' : 'success'}`}
            onClick={() => handleToggleStatus(u)}
          >
            {u.account_status === 'active' ? 'Deactivate' : 'Activate'}
          </button>
        </div>
      ),
    },
  ]

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h4 fw-bold mb-0">User Directory &amp; RBAC</h1>
          <p className="text-muted small mb-0">Manage customer accounts, permissions, and staff credentials.</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => setCreateModal(true)}>
          <i className="bi bi-person-plus me-1" />Create New User
        </button>
      </div>

      <div className="row g-2 mb-3">
        <div className="col-md-6">
          <SearchBar value={search} onChange={setSearch} placeholder="Search users by name or email..." />
        </div>
        <div className="col-md-3">
          <select className="form-select" value={roleFilter} onChange={(e) => { setRoleFilter(e.target.value); setPage(1) }}>
            <option value="">All Roles</option>
            <option value="admin">Administrator</option>
            <option value="agent">Support Agent</option>
            <option value="customer">Customer</option>
          </select>
        </div>
      </div>

      <ErrorMessage error={error} onRetry={reload} />

      <DataTable columns={columns} rows={data?.data || []} loading={loading} rowKey="user_id" />
      <Pagination pagination={data?.pagination} onPage={setPage} />

      {/* Edit User Modal */}
      <Modal
        show={!!editUser}
        title="Edit User Details"
        onClose={() => setEditUser(null)}
        footer={
          <>
            <button className="btn btn-outline-secondary btn-sm" onClick={() => setEditUser(null)}>Cancel</button>
            <button className="btn btn-primary btn-sm" onClick={handleSaveEdit}>Save Changes</button>
          </>
        }
      >
        <div className="mb-3">
          <label className="form-label small fw-medium">Full Name</label>
          <input type="text" className="form-control" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div className="mb-3">
          <label className="form-label small fw-medium">Email</label>
          <input type="email" className="form-control" value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div className="mb-3">
          <label className="form-label small fw-medium">System Role</label>
          <select className="form-select" value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="admin">Admin</option>
            <option value="agent">Agent</option>
            <option value="customer">Customer</option>
          </select>
        </div>
      </Modal>

      {/* Create User Modal */}
      <Modal
        show={createModal}
        title="Create New User Account"
        onClose={() => setCreateModal(false)}
        footer={null}
      >
        <ErrorMessage error={createErr} />
        <form onSubmit={handleCreateUser}>
          <div className="mb-3">
            <label className="form-label small fw-medium">Full Name</label>
            <input required type="text" className="form-control" value={cName} onChange={(e) => setCName(e.target.value)} />
          </div>
          <div className="mb-3">
            <label className="form-label small fw-medium">Email Address</label>
            <input required type="email" className="form-control" value={cEmail} onChange={(e) => setCEmail(e.target.value)} />
          </div>
          <div className="mb-3">
            <label className="form-label small fw-medium">Password</label>
            <input required type="password" className="form-control" value={cPassword} onChange={(e) => setCPassword(e.target.value)} />
            <div className="form-text small">At least 8 characters with letters &amp; numbers</div>
          </div>
          <div className="mb-3">
            <label className="form-label small fw-medium">Account Role</label>
            <select className="form-select" value={cRole} onChange={(e) => setCRole(e.target.value)}>
              <option value="agent">Support Agent</option>
              <option value="customer">Customer</option>
              <option value="admin">Administrator</option>
            </select>
          </div>
          <div className="d-flex justify-content-end gap-2 pt-2 border-top">
            <button type="button" className="btn btn-outline-secondary btn-sm" onClick={() => setCreateModal(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary btn-sm">Create Account</button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
