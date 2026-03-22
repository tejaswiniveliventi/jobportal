import { useState } from 'react'
import { ExternalLink, CheckCircle, XCircle, MapPin, DollarSign, Building2 } from 'lucide-react'
import { useApplications, useApprove, useReject } from '../hooks/useApplications'
import StatusBadge from '../components/StatusBadge'
import ScoreBar from '../components/ScoreBar'
import Spinner from '../components/Spinner'
import type { ApplicationStatus } from '../types'

const TABS: { label: string; status?: ApplicationStatus }[] = [
  { label: 'All' },
  { label: 'Matched',   status: 'scored' },
  { label: 'Queued',    status: 'queued' },
  { label: 'Submitted', status: 'submitted' },
  { label: 'Interview', status: 'interview' },
  { label: 'Offer',     status: 'offer' },
]

export default function Jobs() {
  const [tab, setTab] = useState(0)
  const { data, isLoading } = useApplications(TABS[tab].status)
  const approve = useApprove()
  const reject  = useReject()

  return (
    <div className='p-8'>
      <h1 className='text-2xl font-bold text-gray-900 mb-6'>Applications</h1>

      {/* Tabs */}
      <div className='flex gap-1 border-b border-gray-200 mb-6'>
        {TABS.map((t, i) => (
          <button
            key={i} onClick={() => setTab(i)}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
              tab === i
                ? 'border-b-2 border-brand-600 text-brand-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {isLoading && (
        <div className='flex justify-center py-16'><Spinner size='lg' /></div>
      )}

      {!isLoading && data?.length === 0 && (
        <div className='text-center py-16 text-gray-400'>
          <Building2 className='w-12 h-12 mx-auto mb-3 opacity-30' />
          <p className='text-sm'>No applications in this category yet.</p>
          <p className='text-xs mt-1'>Click "Find new jobs" on the dashboard to start discovery.</p>
        </div>
      )}

      <div className='space-y-3'>
        {data?.map(app => (
          <div key={app.id} className='bg-white rounded-xl border border-gray-200 p-5 hover:border-gray-300 transition-colors'>
            <div className='flex items-start justify-between gap-4'>
              <div className='flex-1 min-w-0'>
                <div className='flex items-center gap-2 flex-wrap'>
                  <h3 className='font-semibold text-gray-900 truncate'>{app.job.title}</h3>
                  <StatusBadge status={app.status} />
                  {app.job.is_remote && (
                    <span className='text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded-full'>Remote</span>
                  )}
                </div>
                <div className='flex items-center gap-4 mt-1 text-sm text-gray-500'>
                  <span className='flex items-center gap-1'>
                    <Building2 className='w-3.5 h-3.5' />{app.job.company}
                  </span>
                  {app.job.location && (
                    <span className='flex items-center gap-1'>
                      <MapPin className='w-3.5 h-3.5' />{app.job.location}
                    </span>
                  )}
                  {(app.job.salary_min || app.job.salary_max) && (
                    <span className='flex items-center gap-1'>
                      <DollarSign className='w-3.5 h-3.5' />
                      {app.job.salary_min ? `$${(app.job.salary_min/1000).toFixed(0)}k` : ''}
                      {app.job.salary_max ? ` – $${(app.job.salary_max/1000).toFixed(0)}k` : ''}
                    </span>
                  )}
                </div>
                {app.match_reasoning && (
                  <p className='text-xs text-gray-400 mt-2 line-clamp-2'>{app.match_reasoning}</p>
                )}
                {app.strengths && app.strengths.length > 0 && (
                  <div className='flex flex-wrap gap-1 mt-2'>
                    {app.strengths.slice(0,3).map((s,i) => (
                      <span key={i} className='text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded-full'>{s}</span>
                    ))}
                  </div>
                )}
              </div>

              <div className='flex flex-col items-end gap-3 shrink-0'>
                <ScoreBar score={app.match_score} />
                <div className='flex items-center gap-2'>
                  <a
                    href={app.job.source_url} target='_blank' rel='noopener noreferrer'
                    className='p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors'
                  >
                    <ExternalLink className='w-4 h-4' />
                  </a>
                  {app.status === 'scored' && (
                    <>
                      <button
                        onClick={() => approve.mutate(app.id)}
                        disabled={approve.isPending}
                        className='flex items-center gap-1.5 px-3 py-1.5 bg-green-50 text-green-700 text-xs font-medium rounded-lg hover:bg-green-100 transition-colors disabled:opacity-50'
                      >
                        <CheckCircle className='w-3.5 h-3.5' />Apply
                      </button>
                      <button
                        onClick={() => reject.mutate(app.id)}
                        disabled={reject.isPending}
                        className='flex items-center gap-1.5 px-3 py-1.5 bg-red-50 text-red-600 text-xs font-medium rounded-lg hover:bg-red-100 transition-colors disabled:opacity-50'
                      >
                        <XCircle className='w-3.5 h-3.5' />Skip
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
