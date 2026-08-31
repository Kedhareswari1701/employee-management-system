export function Spinner() {
  return (
    <div className="spinner-container">
      <div className="spinner" />
    </div>
  )
}

export function Badge({ status }) {
  const map = {
    present: ['badge-success', 'Present'],
    absent: ['badge-danger', 'Absent'],
    late: ['badge-warning', 'Late'],
    half_day: ['badge-purple', 'Half Day'],
    on_leave: ['badge-muted', 'On Leave'],
    pending: ['badge-warning', 'Pending'],
    approved: ['badge-success', 'Approved'],
    rejected: ['badge-danger', 'Rejected'],
    cancelled: ['badge-muted', 'Cancelled'],
    admin: ['badge-purple', 'Admin'],
    manager: ['badge-primary', 'Manager'],
    employee: ['badge-muted', 'Employee'],
  }
  const [cls, label] = map[status] || ['badge-muted', status]
  return <span className={`badge ${cls}`}>{label}</span>
}

export function Alert({ type = 'error', children }) {
  if (!children) return null
  return <div className={`alert alert-${type}`}>{children}</div>
}

export function StatCard({ label, value, color }) {
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-value" style={{ color: color || 'var(--text)' }}>
        {value}
      </div>
    </div>
  )
}

export function EmptyState({ message }) {
  return <div className="empty">{message}</div>
}
