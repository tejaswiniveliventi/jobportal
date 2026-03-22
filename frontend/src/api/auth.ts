import { api } from './client'
import type { User, TokenResponse } from '../types'

export const authApi = {
  register: (email: string, password: string, full_name: string) =>
    api.post<User>('/auth/register', { email, password, full_name }),

  login: async (email: string, password: string): Promise<User> => {
    const { data } = await api.post<TokenResponse>('/auth/login', { email, password })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    const me = await api.get<User>('/auth/me')
    return me.data
  },

  me: () => api.get<User>('/auth/me').then(r => r.data),

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    window.location.href = '/login'
  },
}
