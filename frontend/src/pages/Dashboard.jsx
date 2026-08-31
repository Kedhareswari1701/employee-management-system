import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { Alert, StatCard } from '../components/UI'

export default function Dashboard() {
  const { user } = useAuth()
  const [today, setToday] = useState(null)
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    load()
  }, [])

  const load = async () => {
    try {
      const [todayRes, summaryRes] = await Promise.all([
        api.get('/attendance/today/'),
        api.get('/attendance/summary/'),
      ])
      setToday(todayRes.data)
      setSummary(summaryRes.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load dashboard.')
    }
  }

  const handleCheckIn = async () => {
    try {
      await api.post('/attendance/check_in/', { check_in: new Date().toTimeString().slice(0, 5) })
      load()
    } catch (err) {
      setError(err.response?.data?.errors?.[0]?.message || err.response?.data?.detail || 'Check-in failed.')
    }
  }

  const handleCheckOut = async () => {
    try {
      await api.post('/attendance/check_out/', { check_out: new Date().toTimeString().slice(0, 5) })
      load()
    } catch (err) {
      setError(err.response?.data?.errors?.[0]?.message || err.response?.data?.detail || 'Check-out failed.')
    }
  }

  const firstName = user?.first_name || user?.username

  return (
    <div className="container">
      <h1 className="page-title">Welcome, {firstName}!</h1>
      <p className="page-subtitle">Here's your overview for today.</p>
      <Alert>{error}</Alert>

      <div className="card mb">
        <div className="flex flex-between">
          <div>
            <h3>Today's Attendance</h3>
            {today?.checked_in === false ? (
              <p className="text-muted">You have not checked in yet.</p>
            ) : (
              <p className="text-sm">
                Check-in: <strong>{today?.check_in || '--'}</strong> | Check-out:{' '}
                <strong>{today?.check_out || '--'}</strong> | Status:{' '}
                <strong>{today?.status || '--'}</strong> | Hours:{' '}
                <strong>{today?.worked_hours || 0}</strong>
              </p>
            )}
          </div>
          <div className="flex">
            {(!today || today?.checked_in === false) && (
              <button className="btn btn-success" onClick={handleCheckIn}>
                Check In
              </button>
            )}
            {today && !today.check_out && (
              <button className="btn btn-purple" onClick={handleCheckOut}>
                Check Out
              </button>
            )}
          </div>
        </div>
      </div>

      {summary && (
        <>
          <h3 className="mb">This month's attendance</h3>
          <div className="grid grid-4">
            <StatCard label="Attendance Rate" value={`${summary.attendance_rate}%`} color="var(--primary)" />
            <StatCard label="Present" value={summary.present_days} color="var(--success)" />
            <StatCard label="Late" value={summary.late_days} color="var(--warning)" />
            <StatCard label="Absent" value={summary.absent_days} color="var(--danger)" />
            <StatCard label="Half Days" value={summary.half_days} />
            <StatCard label="On Leave" value={summary.leave_days} />
            <StatCard label="Total Days" value={summary.total_days} />
            <StatCard label="Total Hours" value={summary.total_worked_hours} color="var(--purple)" />
          </div>
        </>
      )}
    </div>
  )
}
