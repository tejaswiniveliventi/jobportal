export interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
  profile_complete: boolean
  preferences: Preferences | null
  automation_settings: AutomationSettings | null
}

export interface Preferences {
  locations?: string[]
  min_salary?: number
  roles?: string[]
  exclude_companies?: string[]
  is_remote_only?: boolean
}

export interface AutomationSettings {
  auto_apply: boolean
  daily_limit: number
  require_approval: boolean
}

export type ApplicationStatus =
  | 'discovered' | 'scored' | 'queued' | 'applying'
  | 'submitted'  | 'tracking' | 'viewed' | 'interview'
  | 'offer'      | 'rejected' | 'withdrawn'

export interface Job {
  id: string
  title: string
  company: string
  location: string | null
  is_remote: boolean
  salary_min: number | null
  salary_max: number | null
  source_url: string
  source_board: string
  posted_at: string | null
}

export interface Application {
  id: string
  user_id: string
  status: ApplicationStatus
  match_score: number | null
  match_reasoning: string | null
  strengths: string[] | null
  gaps: string[] | null
  hiring_manager_name: string | null
  hiring_manager_email: string | null
  applied_at: string | null
  last_status_change: string
  created_at: string
  job: Job
}

export interface DashboardStats {
  total_applications: number
  submitted: number
  interviews: number
  offers: number
  rejected: number
  response_rate: number
  top_companies: { company: string; count: number }[]
  weekly_activity: { date: string; applications: number }[]
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}
