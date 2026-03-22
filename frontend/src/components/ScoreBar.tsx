import clsx from 'clsx'

export default function ScoreBar({ score }: { score: number | null }) {
  if (score === null) return <span className='text-xs text-gray-400'>—</span>
  const pct = Math.round(score * 100)
  const color = pct >= 75 ? 'bg-green-500' : pct >= 55 ? 'bg-yellow-400' : 'bg-red-400'
  return (
    <div className='flex items-center gap-2'>
      <div className='flex-1 bg-gray-200 rounded-full h-1.5 w-20'>
        <div className={clsx('h-1.5 rounded-full', color)} style={{ width: `${pct}%` }} />
      </div>
      <span className='text-xs text-gray-600 w-7 text-right'>{pct}%</span>
    </div>
  )
}
