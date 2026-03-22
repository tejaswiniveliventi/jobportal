import { useState, useRef } from 'react'
import { Upload, CheckCircle, User } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { authApi } from '../api/auth'
import { appApi } from '../api/applications'
import { useUploadResume } from '../hooks/useApplications'
import { setUser } from '../store/authStore'
import Spinner from '../components/Spinner'

export default function Profile() {
  const { data: user, refetch } = useQuery({ queryKey: ['me'], queryFn: authApi.me })
  const upload = useUploadResume()
  const fileRef = useRef<HTMLInputElement>(null)
  const [uploadMsg, setUploadMsg] = useState('')

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setUploadMsg('')
    try {
      await upload.mutateAsync(file)
      setUploadMsg('Resume uploaded! Processing in background…')
      const updated = await authApi.me()
      setUser(updated)
      refetch()
    } catch (err: any) {
      setUploadMsg(err.response?.data?.detail || 'Upload failed')
    }
  }

  const [prefs, setPrefs] = useState({ locations: '', min_salary: '', roles: '' })
  const [saving, setSaving] = useState(false)
  const [savedMsg, setSavedMsg] = useState('')

  async function savePrefs() {
    setSaving(true)
    try {
      const updated = await appApi.updatePreferences({
        locations: prefs.locations ? prefs.locations.split(',').map(s=>s.trim()) : undefined,
        min_salary: prefs.min_salary ? parseInt(prefs.min_salary) : undefined,
        roles: prefs.roles ? prefs.roles.split(',').map(s=>s.trim()) : undefined,
      })
      setUser(updated)
      setSavedMsg('Preferences saved!')
      setTimeout(() => setSavedMsg(''), 3000)
    } finally {
      setSaving(false)
    }
  }

  if (!user) return <div className='flex justify-center p-20'><Spinner size='lg' /></div>

  return (
    <div className='p-8 max-w-2xl space-y-8'>
      <h1 className='text-2xl font-bold text-gray-900'>Profile</h1>

      {/* Identity */}
      <div className='bg-white rounded-xl border border-gray-200 p-6'>
        <div className='flex items-center gap-4 mb-4'>
          <div className='w-12 h-12 bg-brand-100 rounded-full flex items-center justify-center'>
            <User className='w-6 h-6 text-brand-600' />
          </div>
          <div>
            <p className='font-semibold text-gray-900'>{user.full_name}</p>
            <p className='text-sm text-gray-500'>{user.email}</p>
          </div>
        </div>
        <div className='flex items-center gap-2'>
          {user.profile_complete
            ? <><CheckCircle className='w-4 h-4 text-green-500'/><span className='text-sm text-green-600'>Profile complete</span></>
            : <span className='text-sm text-amber-600'>Upload your resume to get started</span>}
        </div>
      </div>

      {/* Resume upload */}
      <div className='bg-white rounded-xl border border-gray-200 p-6'>
        <h2 className='font-semibold text-gray-900 mb-4'>Resume</h2>
        <div
          onClick={() => fileRef.current?.click()}
          className='border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-brand-400 hover:bg-brand-50 transition-colors'
        >
          {upload.isPending
            ? <Spinner size='md' />
            : <>
                <Upload className='w-8 h-8 mx-auto mb-2 text-gray-400' />
                <p className='text-sm font-medium text-gray-700'>Click to upload PDF or Word doc</p>
                <p className='text-xs text-gray-400 mt-1'>Max 10 MB</p>
              </>}
        </div>
        <input ref={fileRef} type='file' accept='.pdf,.doc,.docx' className='hidden' onChange={handleFile} />
        {uploadMsg && <p className='text-sm text-green-600 mt-2'>{uploadMsg}</p>}
      </div>

      {/* Preferences */}
      <div className='bg-white rounded-xl border border-gray-200 p-6'>
        <h2 className='font-semibold text-gray-900 mb-4'>Job preferences</h2>
        <div className='space-y-4'>
          {[
            { key: 'locations', label: 'Locations (comma-separated)', placeholder: 'San Francisco, Remote, New York' },
            { key: 'roles',     label: 'Target roles (comma-separated)', placeholder: 'Software Engineer, Staff Engineer' },
            { key: 'min_salary', label: 'Minimum salary (USD)', placeholder: '120000' },
          ].map(({ key, label, placeholder }) => (
            <div key={key}>
              <label className='block text-sm font-medium text-gray-700 mb-1'>{label}</label>
              <input
                type='text'
                value={(prefs as any)[key]}
                onChange={e => setPrefs(p => ({ ...p, [key]: e.target.value }))}
                placeholder={placeholder}
                className='w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500'
              />
            </div>
          ))}
          <div className='flex items-center justify-between pt-2'>
            <button
              onClick={savePrefs} disabled={saving}
              className='px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50 transition-colors'
            >
              {saving ? 'Saving…' : 'Save preferences'}
            </button>
            {savedMsg && <p className='text-sm text-green-600'>{savedMsg}</p>}
          </div>
        </div>
      </div>
    </div>
  )
}
