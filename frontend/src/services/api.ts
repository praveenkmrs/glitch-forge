/**
 * API Client for HITL Backend
 *
 * Provides typed functions for all backend endpoints.
 */

import axios, { AxiosError, AxiosInstance } from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_V1_PREFIX = '/api/v1'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_URL}${API_V1_PREFIX}`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Types
export interface User {
  id: string
  email: string
  name?: string
  role: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ConsultationRequest {
  id: string
  title: string
  description?: string
  context: Record<string, any>
  state: string
  response?: {
    decision: string
    comment?: string
    responder_id: string
    responded_at: string
  }
  responded_by?: string
  responded_at?: string
  timeout_at?: string
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface APIKey {
  id: string
  name: string
  description?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface APIKeyCreated extends APIKey {
  key: string // Only returned on creation
}

// Auth API
export const authApi = {
  register: async (email: string, password: string, name?: string) => {
    const response = await apiClient.post<User>('/auth/register', {
      email,
      password,
      name,
    })
    return response.data
  },

  login: async (email: string, password: string) => {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)

    const response = await apiClient.post<{ access_token: string; token_type: string }>(
      '/auth/login',
      formData,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    )

    // Save token
    localStorage.setItem('access_token', response.data.access_token)

    return response.data
  },

  getCurrentUser: async () => {
    const response = await apiClient.get<User>('/auth/me')
    // Save user info
    localStorage.setItem('user', JSON.stringify(response.data))
    return response.data
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  },
}

// Requests API
export const requestsApi = {
  list: async (state?: string, limit = 20, offset = 0) => {
    const params = new URLSearchParams()
    if (state) params.append('state', state)
    params.append('limit', limit.toString())
    params.append('offset', offset.toString())

    const response = await apiClient.get<{
      items: ConsultationRequest[]
      total: number
      limit: number
      offset: number
    }>(`/requests?${params}`)

    return response.data
  },

  get: async (id: string) => {
    const response = await apiClient.get<ConsultationRequest>(`/requests/${id}`)
    return response.data
  },

  respond: async (id: string, decision: 'approve' | 'reject' | 'request_changes', comment?: string) => {
    const response = await apiClient.post<ConsultationRequest>(`/requests/${id}/respond`, {
      decision,
      comment,
    })
    return response.data
  },
}

// API Keys API
export const apiKeysApi = {
  create: async (name: string, description?: string) => {
    const response = await apiClient.post<APIKeyCreated>('/api-keys', {
      name,
      description,
    })
    return response.data
  },

  list: async () => {
    const response = await apiClient.get<APIKey[]>('/api-keys')
    return response.data
  },

  get: async (id: string) => {
    const response = await apiClient.get<APIKey>(`/api-keys/${id}`)
    return response.data
  },

  update: async (id: string, data: { name?: string; description?: string; is_active?: boolean }) => {
    const response = await apiClient.patch<APIKey>(`/api-keys/${id}`, data)
    return response.data
  },
}

export default apiClient
