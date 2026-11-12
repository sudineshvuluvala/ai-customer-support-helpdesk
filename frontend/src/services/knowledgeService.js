import { api } from './api'

export const knowledgeService = {
  categories: () => api.get('/knowledge/categories').then((r) => r.data),
  createCategory: (b) => api.post('/knowledge/categories', b).then((r) => r.data),
  updateCategory: (id, b) => api.put(`/knowledge/categories/${id}`, b).then((r) => r.data),
  deleteCategory: (id) => api.del(`/knowledge/categories/${id}`),
  articles: (params) => api.get('/knowledge/articles', params),
  article: (id) => api.get(`/knowledge/articles/${id}`).then((r) => r.data),
  createArticle: (b) => api.post('/knowledge/articles', b).then((r) => r.data),
  updateArticle: (id, b) => api.put(`/knowledge/articles/${id}`, b).then((r) => r.data),
  deleteArticle: (id) => api.del(`/knowledge/articles/${id}`),
}
