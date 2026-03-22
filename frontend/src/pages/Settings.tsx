import { useState } from 'react'
import { appApi } from '../api/applications'
import { authApi } from '../api/auth'
import { setUser } from '../store/authStore'
import { useAuthStore } from '../store/authStore'

export default function Settings() {
  const { user } = useAuthStore()
  const auto = user?.automation_settings
  const [form, setForm] = useState({
    auto_apply:      auto?.auto_apply ?? false,
    daily_limit:     auto?.daily_limit ?? 5,
    require_approval: auto?.require_approval ?? true,
  })
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState('')

  async function save() {
    setSaving(true)
    try {
      const updated = await appApi.updateAutomation(form)
      setUser(updated)
      setMsg('Settings saved!')
      setTimeout(() => setMsg(''), 3000)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className='p-8 max-w-lg'>
      <h1 className='text-2xl font-bold text-gray-900 mb-8'>Settings</h1>

      <div className='bg-white rounded-xl border border-gray-200 p-6 space-y-6'>
        <h2 className='font-semibold text-gray-900'>Automation</h2>

        <label className='flex items-center justify-between'>
          <div>
            <p className='text-sm font-medium text-gray-700'>Auto-apply</p>
            <p className='text-xs text-gray-400'>Apply immediately when you approve a job</p>
          </div>
          <input
            type='checkbox'
            checked={form.auto_apply}
            onChange={e => setForm(f => ({ ...f, auto_apply: e.target.checked }))}
            className='w-4 h-4 text-brand-600 rounded'
          />
        </label>

        <label className='flex items-center justify-between'>
          <div>
            <p className='text-sm font-medium text-gray-700'>Require approval</p>
            <p className='text-xs text-gray-400'>Always ask before applying (recommended)</p>
          </div>
          <input
            type='checkbox'
            checked={form.require_approval}
            onChange={e => setForm(f => ({ ...f, require_approval: e.target.checked }))}
            className='w-4 h-4 text-brand-600 rounded'
          />
        </label>

        <div>
          <label className='block text-sm font-medium text-gray-700 mb-1'>
            Daily application limit
          </label>
          <input
            type='number' min={1} max={50}
            value={form.daily_limit}
            onChange={e => setForm(f => ({ ...f, daily_limit: parseInt(e.target.value) || 5 }))}
            className='w-24 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500'
          />
        </div>

        <div className='flex items-center gap-4 pt-2'>
          <button
            onClick={save} disabled={saving}
            className='px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50 transition-colors'
          >
            {saving ? 'Saving…' : 'Save settings'}
          </button>
          {msg && <p className='text-sm text-green-600'>{msg}</p>}
        </div>
      </div>
    </div>
  )
}
