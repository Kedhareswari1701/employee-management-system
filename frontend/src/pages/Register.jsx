import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { Alert } from '../components/UI'

export default function Register() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [departments, setDepartments] = useState([])
  const [form, setForm] = useState({
    username: '', email: '', first_name: '', last_name: '',
    phone_number: '', department: '', password: '', password2: '',
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (user) navigate('/dashboard')
    api.get('/departments/').then((res) => setDepartments(res.data.results || res.data))
  }, [user, navigate])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      await api.post('/auth/register/', form)
      setSuccess('Registration successful! You can now log in.')
      setTimeout(() => navigate('/login'), 1500)
    } catch (err) {
      const errors = err.response?.data?.errors
      if (errors?.length) {
        setError(errors.map((er) => `${er.field}: ${er.message}`).join('; '))
      } else {
        setError(err.response?.data?.detail || 'Registration failed.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <h1 className="auth-title">Create Account</h1>
        <p className="auth-subtitle">Register as an employee</p>
        <Alert type="success">{success}</Alert>
        <Alert>{error}</Alert>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="label">Username *</label>
            <input className="input" value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })} required />
          </div>
          <div className="form-group">
            <label className="label">Email *</label>
            <input type="email" className="input" value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          </div>
          <div className="grid grid-2">
            <div className="form-group">
              <label className="label">First Name</label>
              <input className="input" value={form.first_name}
                onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
            </div>
            <div className="form-group">
              <label className="label">Last Name</label>
              <input className="input" value={form.last_name}
                onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
            </div>
          </div>
          <div className="form-group">
            <label className="label">Phone Number</label>
            <input className="input" value={form.phone_number}
              onChange={(e) => setForm({ ...form, phone_number: e.target.value })} />
          </div>
          <div className="form-group">
            <label className="label">Department</label>
            <select className="select" value={form.department}
              onChange={(e) => setForm({ ...form, department: e.target.value })}>
              <option value="">Select Department</option>
              {departments.map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          </div>
          <div className="grid grid-2">
            <div className="form-group">
              <label className="label">Password *</label>
              <input type="password" className="input" value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })} required />
            </div>
            <div className="form-group">
              <label className="label">Confirm Password *</label>
              <input type="password" className="input" value={form.password2}
                onChange={(e) => setForm({ ...form, password2: e.target.value })} required />
            </div>
          </div>
          <button className="btn btn-block" disabled={loading}>
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>
        <p className="text-sm mt" style={{ textAlign: 'center' }}>
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
