import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { appApi } from '../api/applications'
import type { ApplicationStatus } from '../types'

export function useDashboard() {
  return useQuery({ queryKey: ['dashboard'], queryFn: appApi.dashboard, refetchInterval: 30_000 })
}

export function useApplications(status?: ApplicationStatus) {
  return useQuery({
    queryKey: ['applications', status],
    queryFn: () => appApi.list(status),
    refetchInterval: 15_000,
  })
}

export function useApprove() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => appApi.approve(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['applications'] }) },
  })
}

export function useReject() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => appApi.reject(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['applications'] }) },
  })
}

export function useDiscover() {
  return useMutation({ mutationFn: appApi.triggerDiscovery })
}

export function useUploadResume() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (file: File) => appApi.uploadResume(file),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['me'] }) },
  })
}
