import { api } from './api'

export const userService = {
  profile: () => api.get('/users/profile').then((r) => r.data),
  updateProfile: (body) => api.put('/users/profile', body).then((r) => r.data),
  uploadAvatar: (file) => {
    const fd = new FormData()
    fd.append('photo', file)
    return api.upload('/users/profile/photo', fd).then((r) => r.data)
  },
  deleteAvatar: () => api.del('/users/profile/photo').then((r) => r.data),
  avatarUrl: (filename) => filename ? `/api/v1/users/avatar/${filename}` : null,
  adminUsers: (params) => api.get('/admin/users', params),
  agents: (params) => api.get('/admin/agents', params),
  agentWorkload: () => api.get('/admin/agents', { workload: 1 }).then((r) => r.data),
  createUser: (body) => api.post('/admin/users', body).then((r) => r.data),
  createAgent: (body) => api.post('/admin/agents', body).then((r) => r.data),
  updateUser: (id, body) => api.put(`/admin/users/${id}`, body).then((r) => r.data),
  setStatus: (id, account_status) => api.patch(`/admin/users/${id}/status`, { account_status }).then((r) => r.data),
  savedReplies: () => api.get('/agents/saved-replies').then((r) => r.data),
  createReply: (b) => api.post('/agents/saved-replies', b).then((r) => r.data),
  updateReply: (id, b) => api.put(`/agents/saved-replies/${id}`, b).then((r) => r.data),
  deleteReply: (id) => api.del(`/agents/saved-replies/${id}`),
}
