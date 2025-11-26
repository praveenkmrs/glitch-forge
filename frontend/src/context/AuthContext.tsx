/**
 * Authentication Context
 *
 * Provides authentication state and functions throughout the app.
 */

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authApi, User } from '@/services/api'

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name?: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // Check if user is logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          const currentUser = await authApi.getCurrentUser()
          setUser(currentUser)
        } catch (error) {
          // Token invalid, clear it
          authApi.logout()
        }
      }
      setLoading(false)
    }

    checkAuth()
  }, [])

  const login = async (email: string, password: string) => {
    await authApi.login(email, password)
    const currentUser = await authApi.getCurrentUser()
    setUser(currentUser)
  }

  const register = async (email: string, password: string, name?: string) => {
    const newUser = await authApi.register(email, password, name)
    // Auto-login after registration
    await login(email, password)
  }

  const logout = () => {
    authApi.logout()
    setUser(null)
    window.location.href = '/login'
  }

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
