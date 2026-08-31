import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { Alert, Badge, EmptyState } from '../components/UI'

export default function LeaveRequests() {
  const { isStaff, user } = useAuth()
  const [requests, setRequests] = useState([])
  const [types, setTypes] = useState([])
  const [users, setUsers] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [form, setForm] = useState({
    leave_type: '', start_date: '', end_date: '', duration_days: '', reason: '',
  })

  const load = async () => {
    try {
      const params = {}
      if (statusFilter) params.status = statusFilter
      const { data } = await api.get('/leaves/requests/', { params })
      setRequests(data.results)
      const typeRes = await api.get('/leaves/types/')
      setTypes(typeRes.data.results || typeRes.data)
      if (isStaff()) {
        const uRes = await api.get('/users/', { params: { page_size: 100 } })
        setUsers(uRes.data.results || uRes.data)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load leave requests.')
    }
  }

  useEffect(() => {
    load()
  }, [statusFilter])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await api.post('/leaves/requests/', form)
      setShowForm(false)
      setForm({ leave_type: '', start_date: '', end_date: '', duration_days: '', reason: '' })
      load()
    } catch (err) {
      const errors = err.response?.data?.errors
      setError(errors?.length ? errors.map((x) => `${x.field}: ${x.message}`).join('; ')
        : err.response?.data?.detail || 'Failed to submit request.')
    }
  }

  const handleReview = async (id, status) => {
    setError('')
    try {
      await api.post(`/leaves/requests/${id}/review/`, { status })
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Review failed.')
    }
  }

  const handleCancel = async (id) => {
    try {
      await api.post(`/leaves/requests/${id}/cancel/`)
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Cancel failed.')
    }
  }

  return (
    <div className="container">
      <div className="flex flex-between">
        <div>
          <h1 className="page-title">Leave Requests</h1>
          <p className="page-subtitle">{isStaff() ? 'Approve or reject requests from your team.' : 'Submit and track your leave.'}</p>
        </div>
        <button className="btn" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Close' : 'New Request'}
        </button>
      </div>

      <Alert>{error}</Alert>

      {showForm && (
        <div className="card mb">
          <h3 className="mb">Submit Leave Request</h3>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-2">
              <div className="form-group">
                <label className="label">Leave Type *</label>
                <select className="select" value={form.leave_type}
                  onChange={(e) => setForm({ ...form, leave_type: e.target.value })} required>
                  <option value="">Select type</option>
                  {types.map((t) => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="label">Duration (days)</label>
                <input type="number" min="1" className="input" value={form.duration_days}
                  onChange={(e) => setForm({ ...form, duration_days: e.target.value })} placeholder="Auto-calculate if empty" />
              </div>
              <div className="form-group">
                <label className="label">Start Date *</label>
                <input type="date" className="input" value={form.start_date}
                  onChange={(e) => setForm({ ...form, start_date: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="label">End Date *</label>
                <input type="date" className="input" value={form.end_date}
                  onChange={(e) => setForm({ ...form, end_date: e.target.value })} required />
              </div>
            </div>
            <div className="form-group">
              <label className="label">Reason *</label>
              <textarea className="textarea" rows="3" value={form.reason}
                onChange={(e) => setForm({ ...form, reason: e.target.value })} required />
            </div>
            <button className="btn btn-success" type="submit">Submit Request</button>
          </form>
        </div>
      )}

      <div className="toolbar">
        <select className="select" style={{ maxWidth: 200 }} value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      <div className="card table-wrap">
        {requests.length === 0 ? (
          <EmptyState message="No leave requests found." />
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Type</th>
                <th>Start</th>
                <th>End</th>
                <th>Days</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((r) => (
                <tr key={r.id}>
                  <td>{r.employee_name}</td>
                  <td>{r.leave_type_name}</td>
                  <td>{r.start_date}</td>
                  <td>{r.end_date}</td>
                  <td>{r.duration_days}</td>
                  <td><Badge status={r.status} /></td>
                  <td>
                    {isStaff() && r.status === 'pending' && (
                      <div className="flex">
                        <button className="btn btn-success" onClick={() => handleReview(r.id, 'approved')}>
                          Approve
                        </button>
                        <button className="btn btn-danger" onClick={() => handleReview(r.id, 'rejected')}>
                          Reject
                        </button>
                      </div>
                    )}
                    {!isStaff() && r.employee === user?.id && r.status === 'pending' && (
                      <button className="btn btn-outline" onClick={() => handleCancel(r.id)}>
                        Cancel
                      </button>
                    )}
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
