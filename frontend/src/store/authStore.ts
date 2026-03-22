import { useState, useEffect } from 'react'
import { authApi } from '../api/auth'
import type { User } from '../types'

// Simple module-level store (no external dep needed)
let _user: User | null = null
const _listeners: Set<() => void> = new Set()

function notify() { _listeners.forEach(fn => fn()) }

export function getUser() { return _user }
export function setUser(u: User | null) { _user = u; notify() }

export function useAuthStore() {
  const [user, setLocalUser] = useState<User | null>(_user)

  useEffect(() => {
    const fn = () => setLocalUser(_user)
    _listeners.add(fn)
    return () => { _listeners.delete(fn) }
  }, [])

  return { user }
}

export async function bootstrapAuth() {
  const token = localStorage.getItem('access_token')
  if (!token) return
  try {
    const u = await authApi.me()
    setUser(u)
  } catch {
    localStorage.clear()
  }
}
