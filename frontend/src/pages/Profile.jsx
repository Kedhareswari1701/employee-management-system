import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { Alert } from '../components/UI'

export default function Profile() {
  const { user, logout, loadProfile } = useAuth()
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [pw, setPw] = useState({ old_password: '', new_password: '' })

  if (!user) return null

  const handlePassword = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    try {
      await api.post('/users/change_password/', pw)
      setPw({ old_password: '', new_password: '' })
      setSuccess('Password changed successfully. Please log in again.')
      setTimeout(() => { logout(); window.location.href = '/login' }, 1200)
    } catch (err) {
      const errors = err.response?.data?.errors
      setError(errors?.length ? errors.map((x) => `${x.field}: ${x.message}`).join('; ')
        : err.response?.data?.detail || 'Password change failed.')
    }
  }

  return (
    <div className="container">
      <h1 className="page-title">My Profile</h1>
      <p className="page-subtitle">Your account details.</p>

      <div className="card mb">
        <div className="grid grid-2">
          <div className="form-group">
            <label className="label">Username</label>
            <input className="input" value={user.username} disabled />
          </div>
          <div className="form-group">
            <label className="label">Email</label>
            <input className="input" value={user.email} disabled />
          </div>
          <div className="form-group">
            <label className="label">Full Name</label>
            <input className="input" value={user.full_name || user.username} disabled />
          </div>
          <div className="form-group">
            <label className="label">Role</label>
            <input className="input" value={user.role} disabled />
          </div>
          <div className="form-group">
            <label className="label">Department</label>
            <input className="input" value={user.department_detail?.name || '--'} disabled />
          </div>
          <div className="form-group">
            <label className="label">Phone</label>
            <input className="input" value={user.phone_number || '--'} disabled />
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="mb">Change Password</h3>
        <Alert>{error}</Alert>
        <Alert type="success">{success}</Alert>
        <form onSubmit={handlePassword}>
          <div className="form-group">
            <label className="label">Current Password</label>
            <input type="password" className="input" value={pw.old_password}
              onChange={(e) => setPw({ ...pw, old_password: e.target.value })} required />
          </div>
          <div className="form-group">
            <label className="label">New Password</label>
            <input type="password" className="input" value={pw.new_password}
              onChange={(e) => setPw({ ...pw, new_password: e.target.value })} required />
          </div>
          <button className="btn" type="submit">Change Password</button>
        </form>
      </div>
    </div>
  )
}
