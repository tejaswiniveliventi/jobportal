import { api } from './client'
import type { Application, ApplicationStatus, DashboardStats, User } from '../types'

export const appApi = {
  list: (status?: ApplicationStatus) =>
    api.get<Application[]>('/applications', { params: status ? { status } : {} }).then(r => r.data),

  dashboard: () =>
    api.get<DashboardStats>('/applications/dashboard').then(r => r.data),

  get: (id: string) =>
    api.get<Application>(`/applications/${id}`).then(r => r.data),

  updateStatus: (id: string, status: ApplicationStatus) =>
    api.patch<Application>(`/applications/${id}/status`, { status }).then(r => r.data),

  approve: (id: string) =>
    api.post(`/jobs/approve/${id}`).then(r => r.data),

  reject: (id: string) =>
    api.post(`/jobs/reject/${id}`).then(r => r.data),

  triggerDiscovery: () =>
    api.post('/jobs/discover').then(r => r.data),

  uploadResume: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/profile/resume', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data)
  },

  updatePreferences: (prefs: object) =>
    api.put<User>('/profile/preferences', prefs).then(r => r.data),

  updateAutomation: (settings: object) =>
    api.put<User>('/profile/automation', settings).then(r => r.data),
}
