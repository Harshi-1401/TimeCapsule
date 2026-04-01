import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Attach JWT token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authAPI = {
  register: (data) => api.post('/auth/signup', data),   // FastAPI endpoint
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me')
};

// ── Rooms ─────────────────────────────────────────────────────────────────────
export const roomAPI = {
  create: (data) => api.post('/rooms/', data),
  getAll: () => api.get('/rooms/'),
  getOne: (id) => api.get(`/rooms/${id}`),
  join: (invite_code) => api.post('/rooms/join', { invite_code }),
  update: (id, data) => api.put(`/rooms/${id}`, data),
  delete: (id) => api.delete(`/rooms/${id}`),
  leave: (id) => api.delete(`/rooms/${id}/leave`)
};

// ── Tasks ─────────────────────────────────────────────────────────────────────
export const taskAPI = {
  create: (roomId, data) => api.post(`/rooms/${roomId}/tasks/`, data),
  getAll: (roomId) => api.get(`/rooms/${roomId}/tasks/`),
  getOne: (roomId, taskId) => api.get(`/rooms/${roomId}/tasks/${taskId}`),
  update: (roomId, taskId, data) => api.put(`/rooms/${roomId}/tasks/${taskId}`, data),
  delete: (roomId, taskId) => api.delete(`/rooms/${roomId}/tasks/${taskId}`)
};

// ── Profile ───────────────────────────────────────────────────────────────────
export const profileAPI = {
  get: () => api.get('/profile/'),
  update: (data) => api.put('/profile/', data),
};

// ── Legacy capsule API (kept for existing pages) ──────────────────────────────
export const capsuleAPI = {
  create: (formData) => api.post('/capsules/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getAll: () => api.get('/capsules/'),
  getOne: (id) => api.get(`/capsules/${id}`),
  getPublic: () => api.get('/capsules/public'),
  delete: (id) => api.delete(`/capsules/${id}`)
};

export default api;
