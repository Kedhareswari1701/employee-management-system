import { useEffect, useState } from 'react'
import api from '../services/api'
import { Alert, Badge, EmptyState } from '../components/UI'

export default function Users() {
  const [users, setUsers] = useState([])
  const [departments, setDepartments] = useState([])
  const [roleFilter, setRoleFilter] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    username: '', email: '', password: '', first_name: '', last_name: '',
    role: 'employee', department: '', manager: '', phone_number: '',
  })

  const load = async () => {
    const params = { page_size: 100 }
    if (roleFilter) params.role = roleFilter
    const res = await api.get('/users/', { params })
    setUsers(res.data.results || res.data)
    const dep = await api.get('/departments/')
    setDepartments(dep.data.results || dep.data)
  }

  useEffect(() => {
    load()
  }, [roleFilter])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await api.post('/users/', form)
      setShowForm(false)
      setForm({ username: '', email: '', password: '', first_name: '', last_name: '',
        role: 'employee', department: '', manager: '', phone_number: '' })
      load()
    } catch (err) {
      const errors = err.response?.data?.errors
      setError(errors?.length ? errors.map((x) => `${x.field}: ${x.message}`).join('; ')
        : err.response?.data?.detail || 'Failed to create user.')
    }
  }

  const toggleActive = async (u) => {
    try {
      await api.patch(`/users/${u.id}/`, { is_active: !u.is_active })
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Update failed.')
    }
  }

  const managers = users.filter((u) => u.role === 'manager')

  return (
    <div className="container">
      <div className="flex flex-between">
        <div>
          <h1 className="page-title">User Management</h1>
          <p className="page-subtitle">Manage employees, managers, and administrators.</p>
        </div>
        <button className="btn" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Close' : 'New User'}
        </button>
      </div>

      <Alert>{error}</Alert>

      {showForm && (
        <div className="card mb">
          <h3 className="mb">Create User</h3>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-2">
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
              <div className="form-group">
                <label className="label">Password *</label>
                <input type="password" className="input" value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="label">Role *</label>
                <select className="select" value={form.role}
                  onChange={(e) => setForm({ ...form, role: e.target.value })}>
                  <option value="employee">Employee</option>
                  <option value="manager">Manager</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
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
              <div className="form-group">
                <label className="label">Department</label>
                <select className="select" value={form.department}
                  onChange={(e) => setForm({ ...form, department: e.target.value })}>
                  <option value="">Select</option>
                  {departments.map((d) => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="label">Manager</label>
                <select className="select" value={form.manager}
                  onChange={(e) => setForm({ ...form, manager: e.target.value })}>
                  <option value="">Select</option>
                  {managers.map((m) => (
                    <option key={m.id} value={m.id}>{m.full_name || m.username}</option>
                  ))}
                </select>
              </div>
            </div>
            <button className="btn btn-success" type="submit">Create User</button>
          </form>
        </div>
      )}

      <div className="toolbar">
        <select className="select" style={{ maxWidth: 200 }} value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}>
          <option value="">All Roles</option>
          <option value="admin">Admin</option>
          <option value="manager">Manager</option>
          <option value="employee">Employee</option>
        </select>
      </div>

      <div className="card table-wrap">
        {users.length === 0 ? (
          <EmptyState message="No users found." />
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Username</th>
                <th>Role</th>
                <th>Department</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.full_name || u.username}</td>
                  <td>{u.username}</td>
                  <td><Badge status={u.role} /></td>
                  <td>{u.department_detail?.name || '--'}</td>
                  <td>{u.is_active ? 'Active' : 'Inactive'}</td>
                  <td>
                    <button className={`btn ${u.is_active ? 'btn-danger' : 'btn-success'}`}
                      onClick={() => toggleActive(u)}>
                      {u.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
