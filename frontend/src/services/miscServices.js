import { api } from './api'

export const dashboardService = {
  admin: () => api.get('/admin/dashboard').then((r) => r.data),
  agent: () => api.get('/agents/dashboard').then((r) => r.data),
  customer: () => api.get('/customer/dashboard').then((r) => r.data),
}

export const analyticsService = {
  overview: () => api.get('/analytics').then((r) => r.data),
  tickets: (days) => api.get('/analytics/tickets', { days }).then((r) => r.data),
  agents: () => api.get('/analytics/agents').then((r) => r.data),
  sla: () => api.get('/analytics/sla').then((r) => r.data),
  reports: (params) => api.get('/admin/reports', params).then((r) => r.data),
  downloadCsv: (params) => api.download(`/admin/reports?format=csv${params.from ? `&from=${params.from}` : ''}${params.to ? `&to=${params.to}` : ''}`, 'tickets_report.csv'),
  auditLogs: (params) => api.get('/admin/audit-logs', params),
  settings: () => api.get('/admin/settings').then((r) => r.data),
  saveSettings: (b) => api.put('/admin/settings', b).then((r) => r.data),
}

export const notificationService = {
  list: (params) => api.get('/notifications', params),
  markRead: (id) => api.patch(`/notifications/${id}/read`),
  markAllRead: () => api.patch('/notifications/read-all'),
}

export const categoryService = {
  list: (params) => api.get('/categories', params).then((r) => r.data),
  create: (b) => api.post('/categories', b).then((r) => r.data),
  update: (id, b) => api.put(`/categories/${id}`, b).then((r) => r.data),
  remove: (id) => api.del(`/categories/${id}`),
}

export const aiService = {
  chat: (message, history) => api.post('/ai/chat', { message, history }).then((r) => r.data),
  classify: (subject, description) => api.post('/ai/classify-ticket', { subject, description }).then((r) => r.data),
  suggestReply: (ticket_id) => api.post('/ai/suggest-reply', { ticket_id }).then((r) => r.data),
  search: (q) => api.get('/ai/search-knowledge', { q }).then((r) => r.data),
}
