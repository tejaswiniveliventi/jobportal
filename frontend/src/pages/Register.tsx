import { useState, FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Zap } from 'lucide-react'
import { authApi } from '../api/auth'
import { setUser } from '../store/authStore'

export default function Register() {
  const nav = useNavigate()
  const [form, setForm] = useState({ email: '', password: '', full_name: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }))

  async function submit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await authApi.register(form.email, form.password, form.full_name)
      const user = await authApi.login(form.email, form.password)
      setUser(user)
      nav('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className='min-h-screen bg-gray-50 flex items-center justify-center p-4'>
      <div className='w-full max-w-sm'>
        <div className='flex items-center justify-center gap-2 mb-8'>
          <Zap className='w-8 h-8 text-brand-600' />
          <span className='text-2xl font-bold text-gray-900'>JobPortal</span>
        </div>
        <div className='bg-white rounded-xl shadow-sm border border-gray-200 p-8'>
          <h1 className='text-xl font-semibold text-gray-900 mb-6'>Create account</h1>
          {error && (
            <div className='mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700'>{error}</div>
          )}
          <form onSubmit={submit} className='space-y-4'>
            {[
              { key: 'full_name', label: 'Full name', type: 'text', placeholder: 'Jane Smith' },
              { key: 'email',     label: 'Email',     type: 'email', placeholder: 'jane@example.com' },
              { key: 'password',  label: 'Password',  type: 'password', placeholder: '8+ chars, 1 upper, 1 number' },
            ].map(({ key, label, type, placeholder }) => (
              <div key={key}>
                <label className='block text-sm font-medium text-gray-700 mb-1'>{label}</label>
                <input
                  type={type} required value={(form as any)[key]} onChange={set(key)}
                  placeholder={placeholder}
                  className='w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500'
                />
              </div>
            ))}
            <button
              type='submit' disabled={loading}
              className='w-full py-2 px-4 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 disabled:opacity-50 transition-colors'
            >
              {loading ? 'Creating…' : 'Create account'}
            </button>
          </form>
          <p className='mt-4 text-center text-sm text-gray-500'>
            Have an account?{' '}
            <Link to='/login' className='text-brand-600 hover:text-brand-700 font-medium'>Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
