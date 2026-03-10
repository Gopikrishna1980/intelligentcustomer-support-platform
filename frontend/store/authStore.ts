import { create } from 'zustand'
import { authApi } from '@/lib/api'

interface User {
  id: string
  email: string
  username: string
  full_name: string
  role: string
  is_agent: boolean
  is_admin: boolean
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  login: (email: string, password: string) => Promise<void>
  register: (data: {
    email: string
    username: string
    full_name: string
    password: string
  }) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await authApi.login(email, password)
      const { access_token, refresh_token, user } = response.data

      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      localStorage.setItem('user', JSON.stringify(user))

      set({ user, isAuthenticated: true, isLoading: false })
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Login failed'
      set({ error: message, isLoading: false })
      throw error
    }
  },

  register: async (data) => {
    set({ isLoading: true, error: null })
    try {
      const response = await authApi.register(data)
      const { access_token, refresh_token, user } = response.data

      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      localStorage.setItem('user', JSON.stringify(user))

      set({ user, isAuthenticated: true, isLoading: false })
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Registration failed'
      set({ error: message, isLoading: false })
      throw error
    }
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    set({ user: null, isAuthenticated: false })
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token')
    const userStr = localStorage.getItem('user')

    if (!token || !userStr) {
      set({ isAuthenticated: false, user: null })
      return
    }

    try {
      const user = JSON.parse(userStr)
      set({ user, isAuthenticated: true })

      // Verify token is still valid
      const response = await authApi.getMe()
      set({ user: response.data })
    } catch (error) {
      // Token is invalid, clear auth
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      set({ user: null, isAuthenticated: false })
    }
  },

  clearError: () => set({ error: null }),
}))
