import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useFetch } from '../../hooks/useFetch'
import { ticketService } from '../../services/ticketService'
import { userService } from '../../services/userService'
import { aiService } from '../../services/miscServices'
import { StatusBadge, PriorityBadge, SlaBadge, fmtDate, STATUSES, PRIORITIES } from '../../utils/format'
import ChatMessage from '../../components/ChatMessage'
import FileUpload from '../../components/FileUpload'
import Modal from '../../components/Modal'
import Loading from '../../components/Loading'
import ErrorMessage from '../../components/ErrorMessage'

export default function TicketDetailPage({ role = 'customer' }) {
  const { id } = useParams()
  const { user } = useAuth()
  const nav = useNavigate()

  // Primary Ticket & Messages Fetch
  const { data: ticket, loading: tLoading, error: tErr, reload: reloadTicket } = useFetch(() => ticketService.get(id), [id])
  const { data: messages, loading: mLoading, reload: reloadMessages } = useFetch(() => ticketService.messages(id), [id])
  const { data: history, reload: reloadHistory } = useFetch(() => ticketService.history(id), [id])

  // Agent workload (for admin assignment)
  const [agents, setAgents] = useState([])
  const [assignModal, setAssignModal] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState('')

  // Message Sending
  const [replyText, setReplyText] = useState('')
  const [msgType, setMsgType] = useState('public')
  const [sending, setSending] = useState(false)
  const [sendErr, setSendErr] = useState(null)
  const [files, setFiles] = useState([])

  // AI Assistant suggested reply (Agent only)
  const [aiSuggestLoading, setAiSuggestLoading] = useState(false)
  const [aiSuggest, setAiSuggest] = useState(null)

  // Saved Replies
  const [savedReplies, setSavedReplies] = useState([])

  const openAssignModal = async () => {
    try {
      const res = await userService.agentWorkload()
      setAgents(res)
      setAssignModal(true)
    } catch (e) {
      alert('Failed to load active agent list.')
    }
  }

  const handleAssign = async () => {
    if (!selectedAgent) return
    try {
      await ticketService.assign(id, selectedAgent, 'Assigned via admin panel')
      setAssignModal(false)
      reloadTicket()
      reloadHistory()
    } catch (e) {
      alert(e.message || 'Assignment failed')
    }
  }

  const handleStatusChange = async (newStatus) => {
    try {
      await ticketService.setStatus(id, newStatus, `Status updated to ${newStatus}`)
      reloadTicket()
      reloadHistory()
    } catch (e) {
      alert(e.message || 'Status transition rejected')
    }
  }

  const handlePriorityChange = async (newPriority) => {
    try {
      await ticketService.setPriority(id, newPriority)
      reloadTicket()
      reloadHistory()
    } catch (e) {
      alert(e.message || 'Priority update rejected')
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!replyText.trim() && files.length === 0) return
    setSending(true)
    setSendErr(null)
    try {
      let createdMsg = null
      if (replyText.trim()) {
        createdMsg = await ticketService.sendMessage(id, replyText, msgType)
      }
      if (files.length > 0) {
        await ticketService.upload(id, files, {
          message_id: createdMsg?.message_id || '',
          is_internal: msgType === 'internal',
        })
        setFiles([])
      }
      setReplyText('')
      reloadMessages()
      reloadTicket()
      reloadHistory()
    } catch (ex) {
      setSendErr(ex)
    } finally {
      setSending(false)
    }
  }

  const loadAiSuggestedReply = async () => {
    setAiSuggestLoading(true)
    try {
      const r = await aiService.suggestReply(id)
      setAiSuggest(r)
    } catch (ex) {
      alert('AI assistant could not generate suggestion: ' + ex.message)
    } finally {
      setAiSuggestLoading(false)
    }
  }

  const loadSavedReplies = async () => {
    try {
      const r = await userService.savedReplies()
      setSavedReplies(r)
    } catch {
      /* ignore */
    }
  }

  if (tLoading) return <Loading text="Loading ticket conversation..." />
  if (tErr) return <ErrorMessage error={tErr} onRetry={reloadTicket} />

  const isClosed = ticket.status === 'closed'

  return (
    <div>
      {/* Top Banner / Breadcrumb */}
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-3 pb-2 border-bottom">
        <div>
          <button className="btn btn-link btn-sm p-0 mb-1 text-decoration-none" onClick={() => nav(`/${role}/tickets`)}>
            <i className="bi bi-arrow-left me-1" />Back to tickets
          </button>
          <div className="d-flex align-items-center gap-2">
            <h1 className="h4 fw-bold mb-0">{ticket.ticket_number}</h1>
            <StatusBadge status={ticket.status} />
            <PriorityBadge priority={ticket.priority} />
            <SlaBadge sla={ticket.sla} />
          </div>
        </div>

        {/* Quick Action Controls */}
        <div className="d-flex flex-wrap gap-2 mt-2 mt-md-0">
          {role === 'admin' && (
            <button className="btn btn-outline-primary btn-sm" onClick={openAssignModal}>
              <i className="bi bi-person-check me-1" />Assign Agent
            </button>
          )}

          {/* Role Status Transitions */}
          {role !== 'customer' && !isClosed && (
            <div className="btn-group btn-group-sm">
              <button className="btn btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                Change Status
              </button>
              <ul className="dropdown-menu dropdown-menu-end shadow">
                {ticket.status !== 'in_progress' && (
                  <li><button className="dropdown-item" onClick={() => handleStatusChange('in_progress')}>In Progress</button></li>
                )}
                {ticket.status !== 'waiting_for_customer' && (
                  <li><button className="dropdown-item" onClick={() => handleStatusChange('waiting_for_customer')}>Waiting for Customer</button></li>
                )}
                {ticket.status !== 'resolved' && (
                  <li><button className="dropdown-item text-success" onClick={() => handleStatusChange('resolved')}>Mark as Resolved</button></li>
                )}
                <li><button className="dropdown-item text-dark" onClick={() => handleStatusChange('closed')}>Close Ticket</button></li>
              </ul>
            </div>
          )}

          {role !== 'customer' && !isClosed && (
            <div className="btn-group btn-group-sm">
              <button className="btn btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                Priority
              </button>
              <ul className="dropdown-menu dropdown-menu-end shadow">
                {PRIORITIES.map((p) => (
                  <li key={p}>
                    <button className="dropdown-item text-capitalize" onClick={() => handlePriorityChange(p)}>{p}</button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {role === 'customer' && ticket.status === 'resolved' && (
            <button className="btn btn-success btn-sm" onClick={() => handleStatusChange('closed')}>
              Confirm &amp; Close Ticket
            </button>
          )}

          {role === 'customer' && isClosed && (
            <button className="btn btn-outline-primary btn-sm" onClick={() => handleStatusChange('open')}>
              Reopen Ticket
            </button>
          )}
        </div>
      </div>

      <div className="row g-4">
        {/* Main Conversation Stream */}
        <div className="col-lg-8">
          {/* Issue Overview Card */}
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-body">
              <h2 className="h5 fw-bold mb-2">{ticket.subject}</h2>
              <p className="text-secondary mb-3" style={{ whiteSpace: 'pre-wrap' }}>{ticket.description}</p>
              <div className="d-flex flex-wrap gap-3 small text-muted border-top pt-2">
                <div><strong>Category:</strong> {ticket.category?.category_name}</div>
                <div><strong>Opened:</strong> {fmtDate(ticket.created_at)}</div>
                {ticket.resolved_at && <div><strong>Resolved:</strong> {fmtDate(ticket.resolved_at)}</div>}
              </div>
            </div>
          </div>

          {/* Conversation History */}
          <h3 className="h6 fw-bold mb-3">Conversation &amp; Updates</h3>
          <div className="chat-thread mb-4">
            {messages?.length === 0 && (
              <div className="text-center text-muted small py-4">No additional replies yet.</div>
            )}
            {messages?.map((m) => (
              <ChatMessage
                key={m.message_id}
                message={m}
                mine={m.sender?.user_id === user?.user_id}
                onDownload={(att) => ticketService.download(att)}
              />
            ))}
          </div>

          {/* AI Suggested Response Box (Agent/Admin) */}
          {role !== 'customer' && !isClosed && (
            <div className="card border-primary-subtle bg-light mb-3">
              <div className="card-body p-3">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <span className="small fw-bold text-primary">
                    <i className="bi bi-robot me-1" />AI Response Copilot
                  </span>
                  <button
                    type="button"
                    disabled={aiSuggestLoading}
                    className="btn btn-sm btn-outline-primary"
                    onClick={loadAiSuggestedReply}
                  >
                    {aiSuggestLoading ? 'Analyzing knowledge base...' : 'Generate AI Suggestion'}
                  </button>
                </div>
                {aiSuggest && (
                  <div className="mt-2 bg-white p-3 rounded border">
                    <div className="small text-secondary mb-2 fst-italic" style={{ whiteSpace: 'pre-wrap' }}>
                      {aiSuggest.suggestion}
                    </div>
                    <div className="d-flex justify-content-between align-items-center pt-2 border-top">
                      <span className="badge text-bg-light border small">Requires agent approval</span>
                      <button
                        type="button"
                        className="btn btn-sm btn-primary"
                        onClick={() => {
                          setReplyText(aiSuggest.suggestion)
                          setAiSuggest(null)
                        }}
                      >
                        Insert Into Reply Composer
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Composer Box */}
          {!isClosed ? (
            <div className="card shadow-sm border-0">
              <div className="card-body">
                <ErrorMessage error={sendErr} />
                <form onSubmit={handleSendMessage}>
                  {role !== 'customer' && (
                    <div className="d-flex gap-3 mb-2 small">
                      <label className="form-check-label fw-medium">
                        <input
                          type="radio"
                          name="mtype"
                          className="form-check-input me-1"
                          checked={msgType === 'public'}
                          onChange={() => setMsgType('public')}
                        />
                        Public Reply to Customer
                      </label>
                      <label className="form-check-label fw-medium text-warning-emphasis">
                        <input
                          type="radio"
                          name="mtype"
                          className="form-check-input me-1"
                          checked={msgType === 'internal'}
                          onChange={() => setMsgType('internal')}
                        />
                        <i className="bi bi-lock-fill me-1" />Internal Note (Staff only)
                      </label>

                      {/* Saved Replies Drawer */}
                      <button
                        type="button"
                        className="btn btn-link btn-sm ms-auto p-0 text-decoration-none"
                        onClick={async () => {
                          await loadSavedReplies()
                          const title = prompt(
                            'Choose saved reply:\n' + savedReplies.map((r, i) => `${i + 1}. ${r.title}`).join('\n')
                          )
                          const idx = parseInt(title, 10) - 1
                          if (savedReplies[idx]) setReplyText(savedReplies[idx].reply_content)
                        }}
                      >
                        <i className="bi bi-chat-square-quote me-1" />Saved Replies
                      </button>
                    </div>
                  )}

                  <div className="mb-3">
                    <textarea
                      rows={4}
                      required={files.length === 0}
                      className={`form-control ${msgType === 'internal' ? 'bg-warning-subtle' : ''}`}
                      placeholder={msgType === 'internal' ? 'Add internal notes hidden from customer...' : 'Type your message to the customer...'}
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                    />
                  </div>

                  <div className="mb-3">
                    <FileUpload files={files} onChange={setFiles} />
                  </div>

                  <div className="d-flex justify-content-end">
                    <button type="submit" disabled={sending} className="btn btn-primary px-4">
                      {sending ? 'Sending...' : msgType === 'internal' ? 'Add Internal Note' : 'Send Response'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          ) : (
            <div className="alert alert-secondary text-center">
              This ticket is closed. Reopen it to resume the conversation.
            </div>
          )}
        </div>

        {/* Sidebar Context Details */}
        <div className="col-lg-4">
          <div className="card shadow-sm border-0 mb-3">
            <div className="card-header bg-white fw-bold">Ticket Information</div>
            <div className="card-body small">
              <div className="mb-2"><strong>Customer:</strong> {ticket.customer?.name.replace(' [SEED]', '')}</div>
              <div className="mb-2"><strong>Email:</strong> {ticket.customer?.email}</div>
              <div className="mb-2">
                <strong>Assigned Agent:</strong>{' '}
                {ticket.assigned_agent ? (
                  ticket.assigned_agent.name.replace(' [SEED]', '')
                ) : (
                  <span className="text-danger fst-italic">Unassigned</span>
                )}
              </div>
              <div className="mb-2"><strong>Target First Response:</strong> {fmtDate(ticket.sla?.response_due_at)}</div>
              <div className="mb-2"><strong>Target Resolution:</strong> {fmtDate(ticket.sla?.resolution_due_at)}</div>
              {ticket.sla?.first_response_at && (
                <div className="mb-2"><strong>First Response:</strong> {fmtDate(ticket.sla?.first_response_at)}</div>
              )}
            </div>
          </div>

          {/* Audit / Status Transition Timeline */}
          <div className="card shadow-sm border-0">
            <div className="card-header bg-white fw-bold">Ticket History</div>
            <div className="card-body p-0">
              <ul className="list-group list-group-flush small">
                {history?.map((h) => (
                  <li key={h.history_id} className="list-group-item">
                    <div className="d-flex justify-content-between text-muted" style={{ fontSize: '0.75rem' }}>
                      <span>{h.changed_by?.name.replace(' [SEED]', '') || 'System'}</span>
                      <span>{fmtDate(h.changed_at)}</span>
                    </div>
                    <div className="fw-semibold mt-1">
                      {h.event_type === 'created' ? (
                        'Ticket Created'
                      ) : h.event_type === 'status' ? (
                        `Status: ${h.old_value} -> ${h.new_value}`
                      ) : h.event_type === 'priority' ? (
                        `Priority: ${h.old_value} -> ${h.new_value}`
                      ) : (
                        `Assigned: ${h.new_value}`
                      )}
                    </div>
                    {h.remarks && <div className="text-secondary">{h.remarks}</div>}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Assignment Modal (Admin only) */}
      <Modal
        show={assignModal}
        title="Assign Support Agent"
        onClose={() => setAssignModal(false)}
        footer={
          <>
            <button className="btn btn-outline-secondary btn-sm" onClick={() => setAssignModal(false)}>Cancel</button>
            <button className="btn btn-primary btn-sm" onClick={handleAssign}>Confirm Assignment</button>
          </>
        }
      >
        <p className="small text-muted">Select an active support agent. Workload and active ticket load are shown below:</p>
        <div className="list-group">
          {agents.map((a) => (
            <label key={a.user_id} className="list-group-item d-flex align-items-center justify-content-between">
              <div>
                <input
                  type="radio"
                  name="agent_sel"
                  className="form-check-input me-2"
                  value={a.user_id}
                  checked={selectedAgent === a.user_id}
                  onChange={() => setSelectedAgent(a.user_id)}
                />
                <span className="fw-semibold">{a.name.replace(' [SEED]', '')}</span>
                <span className="text-muted small ms-2">({a.email})</span>
              </div>
              <span className="badge bg-light text-dark border">{a.active_tickets} active tickets</span>
            </label>
          ))}
        </div>
      </Modal>
    </div>
  )
}
