import { useState } from 'react'
import { categoryService } from '../../services/miscServices'
import { useFetch } from '../../hooks/useFetch'
import DataTable from '../../components/DataTable'
import Modal from '../../components/Modal'
import ErrorMessage from '../../components/ErrorMessage'

export default function CategoryManagementPage() {
  const { data: categories, loading, error, reload } = useFetch(categoryService.list)

  const [modal, setModal] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')
  const [isActive, setIsActive] = useState(true)
  const [modalErr, setModalErr] = useState(null)

  const openCreate = () => {
    setEditingId(null)
    setName('')
    setDesc('')
    setIsActive(true)
    setModalErr(null)
    setModal(true)
  }

  const openEdit = (c) => {
    setEditingId(c.category_id)
    setName(c.category_name)
    setDesc(c.description || '')
    setIsActive(c.is_active)
    setModalErr(null)
    setModal(true)
  }

  const handleSave = async (e) => {
    e.preventDefault()
    setModalErr(null)
    try {
      if (editingId) {
        await categoryService.update(editingId, { category_name: name, description: desc, is_active: isActive })
      } else {
        await categoryService.create({ category_name: name, description: desc, is_active: isActive })
      }
      setModal(false)
      reload()
    } catch (ex) {
      setModalErr(ex)
    }
  }

  const handleDelete = async (cid) => {
    if (!confirm('Are you sure you want to delete this category? (Categories in use cannot be deleted).')) return
    try {
      await categoryService.remove(cid)
      reload()
    } catch (ex) {
      alert(ex.message || 'Category cannot be deleted')
    }
  }

  const columns = [
    { key: 'category_name', label: 'Category Name', render: (c) => <span className="fw-semibold">{c.category_name}</span> },
    { key: 'description', label: 'Description', render: (c) => c.description || '-' },
    {
      key: 'is_active',
      label: 'Status',
      render: (c) => (
        <span className={`badge text-bg-${c.is_active ? 'success' : 'secondary'}`}>
          {c.is_active ? 'Active' : 'Inactive'}
        </span>
      ),
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (c) => (
        <div className="btn-group btn-group-sm">
          <button className="btn btn-outline-secondary" onClick={() => openEdit(c)}>Edit</button>
          <button className="btn btn-outline-danger" onClick={() => handleDelete(c.category_id)}>Delete</button>
        </div>
      ),
    },
  ]

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h4 fw-bold mb-0">Ticket Category Management</h1>
          <p className="text-muted small mb-0">Define support topics, departments, and active inquiry categories.</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={openCreate}>
          <i className="bi bi-plus-circle me-1" />New Category
        </button>
      </div>

      <ErrorMessage error={error} onRetry={reload} />
      <DataTable columns={columns} rows={categories || []} loading={loading} rowKey="category_id" />

      <Modal
        show={modal}
        title={editingId ? 'Edit Ticket Category' : 'Create Ticket Category'}
        onClose={() => setModal(false)}
        footer={null}
      >
        <ErrorMessage error={modalErr} />
        <form onSubmit={handleSave}>
          <div className="mb-3">
            <label className="form-label small fw-medium">Category Name</label>
            <input required type="text" className="form-control" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="mb-3">
            <label className="form-label small fw-medium">Description</label>
            <textarea rows={3} className="form-control" value={desc} onChange={(e) => setDesc(e.target.value)} />
          </div>
          <div className="form-check mb-3">
            <input
              type="checkbox"
              id="cat-active"
              className="form-check-input"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
            />
            <label className="form-check-label small" htmlFor="cat-active">
              Active (Available for customer selection when opening tickets)
            </label>
          </div>
          <div className="d-flex justify-content-end gap-2 pt-2 border-top">
            <button type="button" className="btn btn-outline-secondary btn-sm" onClick={() => setModal(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary btn-sm">{editingId ? 'Save Changes' : 'Create'}</button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
