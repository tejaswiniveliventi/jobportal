import clsx from 'clsx'
import type { ApplicationStatus } from '../types'

const config: Record<ApplicationStatus, { label: string; cls: string }> = {
  discovered: { label: 'Discovered',  cls: 'bg-gray-100 text-gray-700' },
  scored:     { label: 'Matched',     cls: 'bg-blue-100 text-blue-700' },
  queued:     { label: 'Queued',      cls: 'bg-purple-100 text-purple-700' },
  applying:   { label: 'Applying…',   cls: 'bg-yellow-100 text-yellow-700' },
  submitted:  { label: 'Submitted',   cls: 'bg-indigo-100 text-indigo-700' },
  tracking:   { label: 'Tracking',    cls: 'bg-cyan-100 text-cyan-700' },
  viewed:     { label: 'Viewed',      cls: 'bg-sky-100 text-sky-700' },
  interview:  { label: 'Interview',   cls: 'bg-green-100 text-green-700' },
  offer:      { label: 'Offer',       cls: 'bg-emerald-100 text-emerald-700' },
  rejected:   { label: 'Rejected',    cls: 'bg-red-100 text-red-700' },
  withdrawn:  { label: 'Withdrawn',   cls: 'bg-gray-100 text-gray-400' },
}

export default function StatusBadge({ status }: { status: ApplicationStatus }) {
  const { label, cls } = config[status] ?? { label: status, cls: 'bg-gray-100 text-gray-700' }
  return (
    <span className={clsx('inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium', cls)}>
      {label}
    </span>
  )
}
