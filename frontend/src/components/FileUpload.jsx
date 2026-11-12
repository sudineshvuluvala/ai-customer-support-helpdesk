import { useRef, useState } from 'react'
import { fileSize } from '../utils/format'

const ALLOWED = ['pdf', 'png', 'jpg', 'jpeg', 'txt', 'docx']
const MAX_MB = 5

export function validateFiles(list) {
  for (const f of list) {
    const ext = f.name.split('.').pop().toLowerCase()
    if (!ALLOWED.includes(ext)) return `"${f.name}": type .${ext} is not allowed (${ALLOWED.join(', ')}).`
    if (f.size > MAX_MB * 1024 * 1024) return `"${f.name}" exceeds the ${MAX_MB} MB limit.`
  }
  return null
}

export default function FileUpload({ files, onChange, max = 5 }) {
  const input = useRef(null)
  const [drag, setDrag] = useState(false)
  const [err, setErr] = useState(null)

  const add = (incoming) => {
    const list = Array.from(incoming)
    const e = validateFiles(list) || (files.length + list.length > max ? `You can attach at most ${max} files.` : null)
    setErr(e)
    if (!e) onChange([...files, ...list])
  }
  return (
    <div>
      <div className={`dropzone ${drag ? 'drag' : ''}`} role="button" tabIndex={0}
        onClick={() => input.current.click()} onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && input.current.click()}
        onDragOver={(e) => { e.preventDefault(); setDrag(true) }} onDragLeave={() => setDrag(false)}
        onDrop={(e) => { e.preventDefault(); setDrag(false); add(e.dataTransfer.files) }}>
        <i className="bi bi-cloud-arrow-up fs-4" aria-hidden="true" />
        <div>Drag &amp; drop files or <span className="text-primary">browse</span></div>
        <div className="small text-muted">PDF, PNG, JPG, TXT, DOCX · up to {MAX_MB} MB each</div>
        <input ref={input} type="file" multiple hidden accept=".pdf,.png,.jpg,.jpeg,.txt,.docx"
          onChange={(e) => { add(e.target.files); e.target.value = '' }} data-testid="file-input" />
      </div>
      {err && <div className="text-danger small mt-1" role="alert">{err}</div>}
      {files.length > 0 && (
        <ul className="list-unstyled mt-2 mb-0 small">
          {files.map((f, i) => (
            <li key={i} className="d-flex justify-content-between align-items-center py-1 border-bottom">
              <span className="text-truncate"><i className="bi bi-paperclip me-1" />{f.name} <span className="text-muted">({fileSize(f.size)})</span></span>
              <button type="button" className="btn btn-sm btn-link text-danger p-0" onClick={() => onChange(files.filter((_, j) => j !== i))}>Remove</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
