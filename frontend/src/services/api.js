// Central API client: every request to the Flask backend goes through here.
const BASE = import.meta.env.VITE_API_BASE || '/api/v1'
const TOKEN_KEY = 'helpdesk_token'

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (t) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY),
}

export class ApiError extends Error {
  constructor(message, status, code, details) {
    super(message)
    this.status = status
    this.code = code
    this.details = details || {}
  }
}

let onUnauthorized = null
export const setUnauthorizedHandler = (fn) => { onUnauthorized = fn }

function qs(params) {
  if (!params) return ''
  const sp = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') sp.append(k, v)
  })
  const s = sp.toString()
  return s ? `?${s}` : ''
}

async function request(method, path, { params, body, form, raw } = {}) {
  const headers = {}
  const token = tokenStore.get()
  if (token) headers.Authorization = `Bearer ${token}`
  let payload
  if (form) payload = form
  else if (body !== undefined) { headers['Content-Type'] = 'application/json'; payload = JSON.stringify(body) }
  let res
  try {
    res = await fetch(`${BASE}${path}${qs(params)}`, { method, headers, body: payload })
  } catch {
    throw new ApiError('Cannot reach the server. Check your connection and try again.', 0, 'network_error')
  }
  if (raw && res.ok) return res
  let json = null
  try { json = await res.json() } catch { /* non-JSON */ }
  if (!res.ok || (json && json.success === false)) {
    const e = json?.error || {}
    if (res.status === 401 && token && onUnauthorized) onUnauthorized()
    throw new ApiError(e.message || `Request failed (${res.status})`, res.status, e.code, e.details)
  }
  return json
}

export const api = {
  get: (p, params) => request('GET', p, { params }),
  post: (p, body) => request('POST', p, { body }),
  put: (p, body) => request('PUT', p, { body }),
  patch: (p, body) => request('PATCH', p, { body }),
  del: (p) => request('DELETE', p),
  upload: (p, form) => request('POST', p, { form }),
  // authenticated file download (token is sent in the header, never in the URL)
  async download(path, filename) {
    const res = await request('GET', path, { raw: true })
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = filename; document.body.appendChild(a); a.click(); a.remove()
    URL.revokeObjectURL(url)
  },
}
