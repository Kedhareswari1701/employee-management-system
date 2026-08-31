import { createContext, useContext, useEffect, useState } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      loadProfile()
    } else {
      setLoading(false)
    }
  }, [])

  const loadProfile = async () => {
    try {
      const { data } = await api.get('/users/me/')
      setUser(data)
    } catch (err) {
      localStorage.clear()
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    const { data } = await api.post('/token/', { username, password })
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    await loadProfile()
  }

  const logout = () => {
    localStorage.clear()
    setUser(null)
  }

  const isAdmin = () => user?.role === 'admin'
  const isManager = () => user?.role === 'manager'
  const isStaff = () => user?.role === 'admin' || user?.role === 'manager'
  const isEmployee = () => user?.role === 'employee'

  return (
    <AuthContext.Provider
      value={{ user, loading, login, logout, loadProfile, isAdmin, isManager, isStaff, isEmployee }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
