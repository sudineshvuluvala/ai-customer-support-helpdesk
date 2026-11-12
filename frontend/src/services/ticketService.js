import { api } from './api'

export const ticketService = {
  list: (params) => api.get('/tickets', params),
  adminList: (params) => api.get('/admin/tickets', params),
  get: (id) => api.get(`/tickets/${id}`).then((r) => r.data),
  create: (body) => api.post('/tickets', body).then((r) => r.data),
  update: (id, body) => api.put(`/tickets/${id}`, body).then((r) => r.data),
  setStatus: (id, status, remarks) => api.patch(`/tickets/${id}/status`, { status, remarks }).then((r) => r.data),
  setPriority: (id, priority) => api.patch(`/tickets/${id}/priority`, { priority }).then((r) => r.data),
  assign: (id, agent_id, remarks) => api.patch(`/tickets/${id}/assign`, { agent_id, remarks }).then((r) => r.data),
  history: (id) => api.get(`/tickets/${id}/history`).then((r) => r.data),
  messages: (id) => api.get(`/tickets/${id}/messages`).then((r) => r.data),
  sendMessage: (id, message_content, message_type = 'public') =>
    api.post(`/tickets/${id}/messages`, { message_content, message_type }).then((r) => r.data),
  attachments: (id) => api.get(`/tickets/${id}/attachments`).then((r) => r.data),
  upload(id, files, extra = {}) {
    const fd = new FormData()
    files.forEach((f) => fd.append('file', f))
    Object.entries(extra).forEach(([k, v]) => fd.append(k, v))
    return api.upload(`/tickets/${id}/attachments`, fd)
  },
  download: (att) => api.download(`/attachments/${att.attachment_id}/download`, att.original_filename),
  deleteAttachment: (id) => api.del(`/attachments/${id}`),
  categories: (params) => api.get('/categories', params).then((r) => r.data),
}
