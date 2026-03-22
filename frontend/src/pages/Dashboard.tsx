import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { TrendingUp, Send, Calendar, Award, XCircle, RefreshCw } from 'lucide-react'
import { useDashboard, useDiscover } from '../hooks/useApplications'
import Spinner from '../components/Spinner'

const PIE_COLORS = ['#6366f1','#10b981','#f59e0b','#ef4444','#8b5cf6']

function StatCard({ label, value, sub, icon: Icon, color }:
  { label: string; value: number | string; sub?: string; icon: any; color: string }) {
  return (
    <div className='bg-white rounded-xl border border-gray-200 p-5 flex items-start gap-4'>
      <div className={`p-2 rounded-lg ${color}`}>
        <Icon className='w-5 h-5 text-white' />
      </div>
      <div>
        <p className='text-2xl font-bold text-gray-900'>{value}</p>
        <p className='text-sm text-gray-500'>{label}</p>
        {sub && <p className='text-xs text-gray-400 mt-0.5'>{sub}</p>}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { data, isLoading } = useDashboard()
  const discover = useDiscover()

  if (isLoading) return (
    <div className='flex items-center justify-center h-full p-20'>
      <Spinner size='lg' />
    </div>
  )

  if (!data) return null

  return (
    <div className='p-8 space-y-8'>
      {/* Header */}
      <div className='flex items-center justify-between'>
        <h1 className='text-2xl font-bold text-gray-900'>Dashboard</h1>
        <button
          onClick={() => discover.mutate()}
          disabled={discover.isPending}
          className='flex items-center gap-2 px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50 transition-colors'
        >
          <RefreshCw className={`w-4 h-4 ${discover.isPending ? 'animate-spin' : ''}`} />
          {discover.isPending ? 'Discovering…' : 'Find new jobs'}
        </button>
      </div>

      {/* Stat cards */}
      <div className='grid grid-cols-2 lg:grid-cols-5 gap-4'>
        <StatCard label='Total applied'  value={data.total_applications} icon={Send}      color='bg-brand-600' />
        <StatCard label='Submitted'      value={data.submitted}         icon={TrendingUp} color='bg-indigo-500' />
        <StatCard label='Interviews'     value={data.interviews}        icon={Calendar}   color='bg-green-500' />
        <StatCard label='Offers'         value={data.offers}            icon={Award}      color='bg-emerald-500' />
        <StatCard label='Response rate'  value={`${data.response_rate}%`} sub='interviews + offers / submitted' icon={TrendingUp} color='bg-purple-500' />
      </div>

      {/* Charts row */}
      <div className='grid grid-cols-1 lg:grid-cols-3 gap-6'>
        {/* Weekly activity */}
        <div className='lg:col-span-2 bg-white rounded-xl border border-gray-200 p-5'>
          <h2 className='text-sm font-semibold text-gray-700 mb-4'>Weekly activity</h2>
          <ResponsiveContainer width='100%' height={200}>
            <BarChart data={data.weekly_activity}>
              <XAxis dataKey='date' tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
              <Tooltip />
              <Bar dataKey='applications' fill='#6366f1' radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top companies */}
        <div className='bg-white rounded-xl border border-gray-200 p-5'>
          <h2 className='text-sm font-semibold text-gray-700 mb-4'>Top companies</h2>
          {data.top_companies.length === 0 ? (
            <p className='text-sm text-gray-400 text-center py-8'>No applications yet</p>
          ) : (
            <ResponsiveContainer width='100%' height={200}>
              <PieChart>
                <Pie data={data.top_companies} dataKey='count' nameKey='company' cx='50%' cy='50%' outerRadius={80} label={({ company }) => company.slice(0,10)}>
                  {data.top_companies.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v, n) => [v, n]} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  )
}
