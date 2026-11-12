import { fmtDate, fileSize } from '../utils/format'
import UserAvatar from './UserAvatar'

// mine: aligned right. variant: public | internal
export default function ChatMessage({ message, mine, onDownload }) {
  const internal = message.message_type === 'internal'
  const s = message.sender || {}
  return (
    <div className={`chat-row ${mine ? 'mine' : ''}`}>
      {!mine && <UserAvatar user={s} size={32} />}
      <div className={`chat-bubble ${mine ? 'mine' : ''} ${internal ? 'internal' : ''}`}>
        <div className="chat-meta">
          <strong>{(s.name || 'Unknown').replace(' [SEED]', '')}</strong>
          <span className="text-capitalize badge text-bg-light border">{s.role}</span>
          {internal && <span className="badge text-bg-warning"><i className="bi bi-lock-fill me-1" />Internal note</span>}
        </div>
        <div className="chat-text">{message.message_content}</div>
        {message.attachments?.length > 0 && (
          <div className="chat-files">
            {message.attachments.map((a) => (
              <button key={a.attachment_id} className="btn btn-sm btn-outline-secondary" onClick={() => onDownload?.(a)}>
                <i className="bi bi-paperclip" /> {a.original_filename} <span className="text-muted">({fileSize(a.file_size)})</span>
              </button>
            ))}
          </div>
        )}
        <div className="chat-time">{fmtDate(message.created_at)}</div>
      </div>
    </div>
  )
}
