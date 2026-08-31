import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { Badge, EmptyState } from '../components/UI'

export default function Attendance() {
  const { isStaff } = useAuth()
  const [records, setRecords] = useState([])
  const [users, setUsers] = useState([])
  const [filters, setFilters] = useState({ employee: '', status: '' })
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filters.employee) params.employee = filters.employee
      if (filters.status) params.status = filters.status
      const { data } = await api.get('/attendance/', { params })
      setRecords(data.results)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [filters.employee, filters.status])

  useEffect(() => {
    if (isStaff()) {
      api.get('/users/', { params: { page_size: 100 } }).then((res) => setUsers(res.data.results || res.data))
    }
  }, [])

  return (
    <div className="container">
      <div className="flex flex-between">
        <div>
          <h1 className="page-title">Attendance Records</h1>
          <p className="page-subtitle">{isStaff() ? 'View attendance for your department.' : 'Your attendance history.'}</p>
        </div>
      </div>

      <div className="toolbar">
        {isStaff() && (
          <select className="select" style={{ maxWidth: 200 }} value={filters.employee}
            onChange={(e) => setFilters({ ...filters, employee: e.target.value })}>
            <option value="">All Employees</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>{u.full_name || u.username}</option>
            ))}
          </select>
        )}
        <select className="select" style={{ maxWidth: 180 }} value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
          <option value="">All Statuses</option>
          <option value="present">Present</option>
          <option value="absent">Absent</option>
          <option value="late">Late</option>
          <option value="half_day">Half Day</option>
          <option value="on_leave">On Leave</option>
        </select>
      </div>

      <div className="card table-wrap">
        {loading ? (
          <EmptyState message="Loading..." />
        ) : records.length === 0 ? (
          <EmptyState message="No attendance records found." />
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Date</th>
                <th>Check In</th>
                <th>Check Out</th>
                <th>Hours</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r) => (
                <tr key={r.id}>
                  <td>{r.employee_name}</td>
                  <td>{r.date}</td>
                  <td>{r.check_in || '--'}</td>
                  <td>{r.check_out || '--'}</td>
                  <td>{r.worked_hours}</td>
                  <td><Badge status={r.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
