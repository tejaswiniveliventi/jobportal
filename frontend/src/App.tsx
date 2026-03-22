import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Jobs from './pages/Jobs'
import Profile from './pages/Profile'
import Settings from './pages/Settings'
import { bootstrapAuth } from './store/authStore'

export default function App() {
  useEffect(() => { bootstrapAuth() }, [])

  return (
    <Routes>
      <Route path='/login'    element={<Login />} />
      <Route path='/register' element={<Register />} />
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<Dashboard />} />
        <Route path='jobs'     element={<Jobs />} />
        <Route path='profile'  element={<Profile />} />
        <Route path='settings' element={<Settings />} />
      </Route>
      <Route path='*' element={<Navigate to='/' replace />} />
    </Routes>
  )
}
