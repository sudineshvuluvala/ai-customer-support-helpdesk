import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ticketService } from '../../services/ticketService'
import { aiService } from '../../services/miscServices'
import { useFetch } from '../../hooks/useFetch'
import { PRIORITIES } from '../../utils/format'
import FileUpload from '../../components/FileUpload'
import ErrorMessage from '../../components/ErrorMessage'

export default function CreateTicketPage() {
  const nav = useNavigate()
  const { data: categories } = useFetch(ticketService.categories)

  const [subject, setSubject] = useState('')
  const [description, setDescription] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [priority, setPriority] = useState('medium')
  const [files, setFiles] = useState([])

  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState(null)

  // AI Classification suggestion
  const [aiClassifying, setAiClassifying] = useState(false)
  const [aiSuggestion, setAiSuggestion] = useState(null)

  const handleAiClassify = async () => {
    if (!subject.trim() || !description.trim()) {
      alert('Please enter both subject and description before requesting AI classification.')
      return
    }
    setAiClassifying(true)
    try {
      const pred = await aiService.classify(subject, description)
      setAiSuggestion(pred)
      if (pred.category_id) setCategoryId(String(pred.category_id))
      if (pred.priority && pred.priority !== 'critical') setPriority(pred.priority)
    } catch (ex) {
      alert('AI classification is currently unavailable: ' + ex.message)
    } finally {
      setAiClassifying(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErr(null)
    setLoading(true)
    try {
      const ticket = await ticketService.create({
        subject,
        description,
        category_id: categoryId,
        priority,
      })
      if (files.length > 0) {
        await ticketService.upload(ticket.ticket_id, files)
      }
      nav(`/customer/tickets/${ticket.ticket_id}`)
    } catch (ex) {
      setErr(ex)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="row justify-content-center">
      <div className="col-lg-8">
        <div className="card shadow-sm border-0">
          <div className="card-header bg-white p-4 pb-0 border-0">
            <h1 className="h4 fw-bold mb-1">Create Support Ticket</h1>
            <p className="text-muted small">Submit your inquiry or technical issue to our customer care team.</p>
          </div>
          <div className="card-body p-4 pt-2">
            <ErrorMessage error={err} />

            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label className="form-label small fw-medium">Subject / Short Summary</label>
                <input
                  type="text"
                  required
                  minLength={5}
                  maxLength={200}
                  className="form-control"
                  placeholder="e.g. Cannot log in after password change"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                />
              </div>

              <div className="mb-3">
                <label className="form-label small fw-medium">Detailed Issue Description</label>
                <textarea
                  rows={5}
                  required
                  minLength={10}
                  maxLength={10000}
                  className="form-control"
                  placeholder="Explain what happened, steps to reproduce, or any error messages..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>

              {/* AI Classification Copilot Button */}
              <div className="mb-4">
                <button
                  type="button"
                  disabled={aiClassifying}
                  className="btn btn-outline-primary btn-sm"
                  onClick={handleAiClassify}
                >
                  <i className="bi bi-magic me-1" />
                  {aiClassifying ? 'Analyzing text...' : 'AI Auto-Detect Category & Priority'}
                </button>
                {aiSuggestion && (
                  <div className="alert alert-info py-2 px-3 mt-2 small">
                    <strong>AI Suggestion:</strong> Categorized as <strong>{aiSuggestion.category_name}</strong> with{' '}
                    <strong>{aiSuggestion.priority}</strong> priority ({aiSuggestion.note})
                  </div>
                )}
              </div>

              <div className="row g-3 mb-3">
                <div className="col-md-6">
                  <label className="form-label small fw-medium">Category</label>
                  <select
                    required
                    className="form-select"
                    value={categoryId}
                    onChange={(e) => setCategoryId(e.target.value)}
                  >
                    <option value="">Select a Category...</option>
                    {categories?.map((c) => (
                      <option key={c.category_id} value={c.category_id}>
                        {c.category_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="col-md-6">
                  <label className="form-label small fw-medium">Priority</label>
                  <select
                    className="form-select text-capitalize"
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                  >
                    {PRIORITIES.filter((p) => p !== 'critical').map((p) => (
                      <option key={p} value={p}>
                        {p}
                      </option>
                    ))}
                  </select>
                  <div className="form-text small">High priority is reserved for urgent or blocking issues.</div>
                </div>
              </div>

              <div className="mb-4">
                <label className="form-label small fw-medium">Supporting Attachments (Optional)</label>
                <FileUpload files={files} onChange={setFiles} />
              </div>

              <div className="d-flex justify-content-end gap-2">
                <button type="button" className="btn btn-outline-secondary" onClick={() => nav('/customer/tickets')}>
                  Cancel
                </button>
                <button type="submit" disabled={loading} className="btn btn-primary px-4">
                  {loading ? 'Submitting...' : 'Submit Ticket'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
