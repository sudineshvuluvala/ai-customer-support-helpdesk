import { useState } from 'react'
import { userService } from '../../services/userService'
import { useFetch } from '../../hooks/useFetch'
import DataTable from '../../components/DataTable'
import Modal from '../../components/Modal'
import ErrorMessage from '../../components/ErrorMessage'

export default function SavedRepliesPage() {
  const { data: replies, loading, error, reload } = useFetch(userService.savedReplies)

  const [modal, setModal] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [modalErr, setModalErr] = useState(null)

  const openCreate = () => {
    setEditingId(null)
    setTitle('')
    setContent('')
    setModalErr(null)
    setModal(true)
  }

  const openEdit = (r) => {
    setEditingId(r.reply_id)
    setTitle(r.title)
    setContent(r.reply_content)
    setModalErr(null)
    setModal(true)
  }

  const handleSave = async (e) => {
    e.preventDefault()
    setModalErr(null)
    try {
      if (editingId) {
        await userService.updateReply(editingId, { title, reply_content: content })
      } else {
        await userService.createReply({ title, reply_content: content })
      }
      setModal(false)
      reload()
    } catch (ex) {
      setModalErr(ex)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this saved reply template?')) return
    try {
      await userService.deleteReply(id)
      reload()
    } catch (ex) {
      alert(ex.message || 'Deletion failed')
    }
  }

  const columns = [
    { key: 'title', label: 'Template Title', render: (r) => <span className="fw-semibold">{r.title}</span> },
    { key: 'reply_content', label: 'Snippet Content', render: (r) => <span className="small text-secondary">{r.reply_content}</span> },
    {
      key: 'actions',
      label: 'Actions',
      render: (r) => (
        <div className="btn-group btn-group-sm">
          <button className="btn btn-outline-secondary" onClick={() => openEdit(r)}>Edit</button>
          <button className="btn btn-outline-danger" onClick={() => handleDelete(r.reply_id)}>Delete</button>
        </div>
      ),
    },
  ]

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h4 fw-bold mb-0">Canned / Saved Replies</h1>
          <p className="text-muted small mb-0">Quick reply templates to speed up agent communication and customer responses.</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={openCreate}>
          <i className="bi bi-plus-circle me-1" />New Template
        </button>
      </div>

      <ErrorMessage error={error} onRetry={reload} />
      <DataTable columns={columns} rows={replies || []} loading={loading} rowKey="reply_id" />

      <Modal
        show={modal}
        title={editingId ? 'Edit Saved Reply' : 'Create Saved Reply Template'}
        onClose={() => setModal(false)}
        footer={null}
      >
        <ErrorMessage error={modalErr} />
        <form onSubmit={handleSave}>
          <div className="mb-3">
            <label className="form-label small fw-medium">Template Title</label>
            <input required type="text" className="form-control" value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="mb-3">
            <label className="form-label small fw-medium">Canned Response Content</label>
            <textarea
              rows={5}
              required
              className="form-control"
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />
          </div>
          <div className="d-flex justify-content-end gap-2 pt-2 border-top">
            <button type="button" className="btn btn-outline-secondary btn-sm" onClick={() => setModal(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary btn-sm">{editingId ? 'Save Template' : 'Create'}</button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
