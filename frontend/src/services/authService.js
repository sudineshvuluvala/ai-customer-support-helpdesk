import { api, tokenStore } from './api'

export const authService = {
  async login(email, password) {
    const r = await api.post('/auth/login', { email, password })
    tokenStore.set(r.data.token)
    return r.data.user
  },
  register: (name, email, password) => api.post('/auth/register', { name, email, password }),
  forgotPassword: (email) => api.post('/auth/forgot-password', { email }),
  resetPassword: (token, password) => api.post('/auth/reset-password', { token, password }),
  async logout() {
    try { await api.post('/auth/logout') } finally { tokenStore.clear() }
  },
  me: () => api.get('/auth/me').then((r) => r.data),
}
