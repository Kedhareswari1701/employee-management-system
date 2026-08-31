import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { Alert, EmptyState } from '../components/UI'

export default function Departments() {
  const { isStaff } = useAuth()
  const [departments, setDepartments] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ name: '', code: '', description: '' })

  const load = async () => {
    const res = await api.get('/departments/')
    setDepartments(res.data.results || res.data)
  }

  useEffect(() => {
    load()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await api.post('/departments/', form)
      setShowForm(false)
      setForm({ name: '', code: '', description: '' })
      load()
    } catch (err) {
      const errors = err.response?.data?.errors
      setError(errors?.length ? errors.map((x) => `${x.field}: ${x.message}`).join('; ')
        : err.response?.data?.detail || 'Failed to create department.')
    }
  }

  return (
    <div className="container">
      <div className="flex flex-between">
        <div>
          <h1 className="page-title">Departments</h1>
          <p className="page-subtitle">Organizational units in the company.</p>
        </div>
        {isStaff() && (
          <button className="btn" onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Close' : 'New Department'}
          </button>
        )}
      </div>

      <Alert>{error}</Alert>

      {showForm && isStaff() && (
        <div className="card mb">
          <h3 className="mb">Create Department</h3>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-2">
              <div className="form-group">
                <label className="label">Name *</label>
                <input className="input" value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="label">Code *</label>
                <input className="input" value={form.code}
                  onChange={(e) => setForm({ ...form, code: e.target.value })} required />
              </div>
            </div>
            <div className="form-group">
              <label className="label">Description</label>
              <textarea className="textarea" rows="2" value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })} />
            </div>
            <button className="btn btn-success" type="submit">Create</button>
          </form>
        </div>
      )}

      <div className="card table-wrap">
        {departments.length === 0 ? (
          <EmptyState message="No departments found." />
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Code</th>
                <th>Description</th>
                <th>Employees</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {departments.map((d) => (
                <tr key={d.id}>
                  <td><strong>{d.name}</strong></td>
                  <td>{d.code}</td>
                  <td className="text-sm text-muted">{d.description || '--'}</td>
                  <td>{d.employee_count}</td>
                  <td>{d.is_active ? 'Active' : 'Inactive'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
