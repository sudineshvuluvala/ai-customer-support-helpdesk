import { useState } from 'react'
import { knowledgeService } from '../../services/knowledgeService'
import { useFetch, useDebounce } from '../../hooks/useFetch'
import DataTable from '../../components/DataTable'
import SearchBar from '../../components/SearchBar'
import Pagination from '../../components/Pagination'
import Modal from '../../components/Modal'
import ErrorMessage from '../../components/ErrorMessage'
import { fmtDate } from '../../utils/format'

export default function KnowledgeAdminPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const debouncedSearch = useDebounce(search, 300)

  const { data: categories } = useFetch(knowledgeService.categories)
  const { data, loading, error, reload } = useFetch(
    () => knowledgeService.articles({ page, per_page: 10, q: debouncedSearch || undefined, status: statusFilter || undefined }),
    [page, debouncedSearch, statusFilter]
  )

  // Article Modal state
  const [modal, setModal] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [status, setStatus] = useState('published')
  const [modalErr, setModalErr] = useState(null)

  const openCreate = () => {
    setEditingId(null)
    setTitle('')
    setContent('')
    setCategoryId(categories?.[0]?.category_id ? String(categories[0].category_id) : '')
    setStatus('published')
    setModalErr(null)
    setModal(true)
  }

  const openEdit = async (art) => {
    try {
      const full = await knowledgeService.article(art.article_id)
      setEditingId(full.article_id)
      setTitle(full.title)
      setContent(full.content)
      setCategoryId(String(full.category?.category_id || ''))
      setStatus(full.status)
      setModalErr(null)
      setModal(true)
    } catch (e) {
      alert('Could not load full article: ' + e.message)
    }
  }

  const handleSave = async (e) => {
    e.preventDefault()
    setModalErr(null)
    try {
      const payload = { title, content, category_id: categoryId, status }
      if (editingId) {
        await knowledgeService.updateArticle(editingId, payload)
      } else {
        await knowledgeService.createArticle(payload)
      }
      setModal(false)
      reload()
    } catch (ex) {
      setModalErr(ex)
    }
  }

  const handleDelete = async (aid) => {
    if (!confirm('Are you sure you want to delete this article?')) return
    try {
      await knowledgeService.deleteArticle(aid)
      reload()
    } catch (ex) {
      alert(ex.message || 'Deletion failed')
    }
  }

  const columns = [
    { key: 'title', label: 'Title', render: (a) => <span className="fw-semibold">{a.title}</span> },
    { key: 'category', label: 'Category', render: (a) => a.category?.category_name || '-' },
    {
      key: 'status',
      label: 'Status',
      render: (a) => (
        <span className={`badge text-bg-${a.status === 'published' ? 'success' : a.status === 'draft' ? 'warning' : 'secondary'}`}>
          {a.status}
        </span>
      ),
    },
    { key: 'updated_at', label: 'Last Modified', render: (a) => <span className="small text-muted">{fmtDate(a.updated_at)}</span> },
    {
      key: 'actions',
      label: 'Actions',
      render: (a) => (
        <div className="btn-group btn-group-sm">
          <button className="btn btn-outline-secondary" onClick={() => openEdit(a)}>Edit</button>
          <button className="btn btn-outline-danger" onClick={() => handleDelete(a.article_id)}>Delete</button>
        </div>
      ),
    },
  ]

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h4 fw-bold mb-0">Knowledge Base Management</h1>
          <p className="text-muted small mb-0">Publish troubleshooting guides, FAQs, and AI grounding documentation.</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={openCreate}>
          <i className="bi bi-file-earmark-plus me-1" />New Article
        </button>
      </div>

      <div className="row g-2 mb-3">
        <div className="col-md-6">
          <SearchBar value={search} onChange={setSearch} placeholder="Search articles..." />
        </div>
        <div className="col-md-3">
          <select className="form-select" value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}>
            <option value="">All Statuses</option>
            <option value="published">Published</option>
            <option value="draft">Draft</option>
            <option value="archived">Archived</option>
          </select>
        </div>
      </div>

      <ErrorMessage error={error} onRetry={reload} />
      <DataTable columns={columns} rows={data?.data || []} loading={loading} rowKey="article_id" />
      <Pagination pagination={data?.pagination} onPage={setPage} />

      <Modal
        show={modal}
        size="modal-lg"
        title={editingId ? 'Edit Knowledge Article' : 'Create Knowledge Article'}
        onClose={() => setModal(false)}
        footer={null}
      >
        <ErrorMessage error={modalErr} />
        <form onSubmit={handleSave}>
          <div className="mb-3">
            <label className="form-label small fw-medium">Article Title</label>
            <input required type="text" className="form-control" value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="row g-3 mb-3">
            <div className="col-md-6">
              <label className="form-label small fw-medium">Category</label>
              <select required className="form-select" value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
                <option value="">Select Category...</option>
                {categories?.map((c) => (
                  <option key={c.category_id} value={c.category_id}>{c.category_name}</option>
                ))}
              </select>
            </div>
            <div className="col-md-6">
              <label className="form-label small fw-medium">Publishing Status</label>
              <select className="form-select" value={status} onChange={(e) => setStatus(e.target.value)}>
                <option value="published">Published (Visible to customers &amp; AI)</option>
                <option value="draft">Draft (Staff review only)</option>
                <option value="archived">Archived</option>
              </select>
            </div>
          </div>
          <div className="mb-3">
            <label className="form-label small fw-medium">Content (Markdown or Plain Text)</label>
            <textarea
              rows={8}
              required
              className="form-control font-monospace small"
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />
          </div>
          <div className="d-flex justify-content-end gap-2 pt-2 border-top">
            <button type="button" className="btn btn-outline-secondary btn-sm" onClick={() => setModal(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary btn-sm">{editingId ? 'Save Article' : 'Publish Article'}</button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
