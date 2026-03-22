import { NavLink, Outlet } from 'react-router-dom'
import { LayoutDashboard, Briefcase, User, Settings, LogOut, Zap } from 'lucide-react'
import { authApi } from '../api/auth'
import { useAuthStore } from '../store/authStore'

const nav = [
  { to: '/',            label: 'Dashboard',    icon: LayoutDashboard },
  { to: '/jobs',        label: 'Jobs',         icon: Briefcase },
  { to: '/profile',     label: 'Profile',      icon: User },
  { to: '/settings',    label: 'Settings',     icon: Settings },
]

export default function Layout() {
  const { user } = useAuthStore()

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-60 bg-white border-r border-gray-200 flex flex-col py-6 px-4">
        <div className="flex items-center gap-2 px-2 mb-8">
          <Zap className="w-6 h-6 text-brand-600" />
          <span className="font-bold text-gray-900 text-lg">JobPortal</span>
        </div>

        <nav className="flex-1 space-y-1">
          {nav.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to} to={to} end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-brand-50 text-brand-700'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-gray-200 pt-4">
          <p className="text-xs text-gray-500 px-3 mb-1 truncate">{user?.email}</p>
          <button
            onClick={authApi.logout}
            className="flex items-center gap-3 px-3 py-2 w-full text-sm text-gray-600 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
