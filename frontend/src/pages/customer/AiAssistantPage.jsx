import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { aiService } from '../../services/miscServices'

export default function AiAssistantPage() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I am your AI Helpdesk Assistant. Ask me any question about our services, policies, account issues, or how to use the helpdesk.',
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const threadEndRef = useRef(null)

  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMsg = input.trim()
    setInput('')
    const updatedHistory = [...messages, { role: 'user', content: userMsg }]
    setMessages(updatedHistory)
    setLoading(true)

    try {
      const res = await aiService.chat(userMsg, updatedHistory.slice(0, -1))
      setMessages([
        ...updatedHistory,
        {
          role: 'assistant',
          content: res.answer,
          articles: res.articles,
          suggest_ticket: res.suggest_ticket,
          source: res.source,
        },
      ])
    } catch (ex) {
      setMessages([
        ...updatedHistory,
        {
          role: 'assistant',
          content: 'I apologize, but I encountered a temporary connection issue. Please create a support ticket if your issue is urgent.',
          suggest_ticket: true,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="row justify-content-center">
      <div className="col-lg-8">
        <div className="card shadow-sm border-0 d-flex flex-column" style={{ height: '78vh' }}>
          {/* Header */}
          <div className="card-header bg-white p-3 border-bottom d-flex align-items-center justify-content-between">
            <div className="d-flex align-items-center gap-2">
              <div className="avatar bg-primary text-white"><i className="bi bi-robot" /></div>
              <div>
                <h1 className="h6 fw-bold mb-0">AI Customer Support FAQ Assistant</h1>
                <span className="small text-muted" style={{ fontSize: '0.75rem' }}>
                  Natural-language answers grounded strictly in published knowledge articles
                </span>
              </div>
            </div>
            <Link to="/customer/tickets/create" className="btn btn-outline-primary btn-sm">
              <i className="bi bi-ticket-perforated me-1" />Open Ticket Instead
            </Link>
          </div>

          {/* Conversation Stream */}
          <div className="card-body p-3 overflow-y-auto flex-grow-1" style={{ background: '#f8fafc' }}>
            <div className="d-flex flex-column gap-3">
              {messages.map((m, idx) => (
                <div key={idx} className={`d-flex ${m.role === 'user' ? 'justify-content-end' : 'justify-content-start'}`}>
                  <div
                    className={`p-3 rounded-3 shadow-sm ${
                      m.role === 'user' ? 'bg-primary text-white' : 'bg-white border'
                    }`}
                    style={{ maxWidth: '80%' }}
                  >
                    <div className="small" style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>

                    {/* Cited / Recommended Knowledge Articles */}
                    {m.articles && m.articles.length > 0 && (
                      <div className="mt-2 pt-2 border-top text-dark">
                        <div className="small fw-semibold mb-1 text-muted">Related Knowledge Base Articles:</div>
                        <div className="d-flex flex-column gap-1">
                          {m.articles.map((art) => (
                            <Link
                              key={art.article_id}
                              to={`/customer/knowledge/${art.article_id}`}
                              className="text-decoration-none small text-primary p-1 bg-light rounded border d-block"
                            >
                              <i className="bi bi-file-earmark-text me-1" />
                              {art.title}
                            </Link>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Ticket Suggestion Call to Action */}
                    {m.suggest_ticket && (
                      <div className="mt-2 pt-2 border-top">
                        <Link to="/customer/tickets/create" className="btn btn-primary btn-sm w-100">
                          <i className="bi bi-plus-circle me-1" />Create Support Ticket
                        </Link>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="d-flex justify-content-start">
                  <div className="bg-white border p-3 rounded-3 text-muted small d-flex align-items-center gap-2">
                    <span className="spinner-grow spinner-grow-sm text-primary" />
                    Searching knowledge base and formulating response...
                  </div>
                </div>
              )}
              <div ref={threadEndRef} />
            </div>
          </div>

          {/* Prompt Input Form */}
          <div className="card-footer bg-white p-3 border-top">
            <form onSubmit={handleSend} className="d-flex gap-2">
              <input
                type="text"
                required
                className="form-control"
                placeholder="Ask a question (e.g., 'How do I reset my password?' or 'What are the file upload limits?')"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={loading}
              />
              <button type="submit" disabled={loading || !input.trim()} className="btn btn-primary px-3">
                <i className="bi bi-send" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
