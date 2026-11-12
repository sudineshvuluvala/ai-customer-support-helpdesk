export const STATUS_LABEL = {
  open: 'Open', assigned: 'Assigned', in_progress: 'In Progress',
  waiting_for_customer: 'Waiting for Customer', resolved: 'Resolved', closed: 'Closed',
}
export const STATUS_COLOR = {
  open: 'primary', assigned: 'info', in_progress: 'warning', waiting_for_customer: 'secondary', resolved: 'success', closed: 'dark',
}
export const PRIORITY_COLOR = { low: 'secondary', medium: 'info', high: 'warning', critical: 'danger' }
export const SLA_COLOR = { on_track: 'success', at_risk: 'warning', breached: 'danger', met: 'success' }
export const SLA_LABEL = { on_track: 'On track', at_risk: 'At risk', breached: 'Breached', met: 'Met' }
export const STATUSES = Object.keys(STATUS_LABEL)
export const PRIORITIES = ['low', 'medium', 'high', 'critical']

export const StatusBadge = ({ status }) => (
  <span className={`badge rounded-pill text-bg-${STATUS_COLOR[status] || 'light'}`}>{STATUS_LABEL[status] || status}</span>
)
export const PriorityBadge = ({ priority }) => (
  <span className={`badge text-bg-${PRIORITY_COLOR[priority] || 'light'} text-capitalize`}>{priority}</span>
)
export const SlaBadge = ({ sla }) =>
  sla ? <span className={`badge badge-soft-${SLA_COLOR[sla.sla_status]}`}>{SLA_LABEL[sla.sla_status]}</span> : null

export function fmtDate(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
}

export function timeAgo(iso) {
  if (!iso) return ''
  const s = Math.max(1, Math.floor((Date.now() - new Date(iso).getTime()) / 1000))
  if (s < 60) return 'just now'
  const m = Math.floor(s / 60); if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60); if (h < 24) return `${h}h ago`
  const d = Math.floor(h / 24); if (d < 30) return `${d}d ago`
  return fmtDate(iso)
}

export function remaining(iso) {
  if (!iso) return ''
  const diff = new Date(iso).getTime() - Date.now()
  const abs = Math.abs(diff)
  const h = Math.floor(abs / 3600000), m = Math.floor((abs % 3600000) / 60000)
  const txt = h >= 48 ? `${Math.floor(h / 24)}d ${h % 24}h` : `${h}h ${m}m`
  return diff >= 0 ? `${txt} left` : `${txt} overdue`
}

export function fileSize(n) {
  if (n < 1024) return `${n} B`
  if (n < 1048576) return `${(n / 1024).toFixed(1)} KB`
  return `${(n / 1048576).toFixed(1)} MB`
}

export const initials = (name = '') => name.replace(/\[.*?\]/g, '').trim().split(/\s+/).slice(0, 2).map((p) => p[0]?.toUpperCase()).join('') || '?'
