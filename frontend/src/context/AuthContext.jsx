import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { authService } from '../services/authService'
import { setUnauthorizedHandler, tokenStore } from '../services/api'

const AuthContext = createContext(null)
export const useAuth = () => useContext(AuthContext)

export const homeFor = (role) => ({ admin: '/admin', agent: '/agent', customer: '/customer' }[role] || '/login')

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(!!tokenStore.get())
  const [notice, setNotice] = useState('')

  const clear = useCallback((msg) => {
    tokenStore.clear(); setUser(null)
    if (msg) setNotice(msg)
  }, [])

  useEffect(() => { setUnauthorizedHandler(() => clear('Your session has expired. Please log in again.')) }, [clear])

  useEffect(() => {
    if (!tokenStore.get()) return
    authService.me().then(setUser).catch(() => clear()).finally(() => setLoading(false))
  }, [clear])

  const login = async (email, password) => {
    const u = await authService.login(email, password)
    setNotice(''); setUser(u)
    return u
  }
  const logout = async () => { try { await authService.logout() } catch { /* ignore */ } clear() }
  const value = useMemo(() => ({ user, loading, login, logout, notice, setUser, clearNotice: () => setNotice('') }), [user, loading, notice]) // eslint-disable-line
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
