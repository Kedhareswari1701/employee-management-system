import { useEffect, useState } from 'react'
import api from '../services/api'
import { EmptyState } from '../components/UI'

export default function LeaveBalances() {
  const [balances, setBalances] = useState([])

  useEffect(() => {
    api.get('/leaves/balances/').then((res) => setBalances(res.data.results || res.data))
  }, [])

  return (
    <div className="container">
      <h1 className="page-title">Leave Balances</h1>
      <p className="page-subtitle">Your available leave days per type.</p>

      <div className="card table-wrap">
        {balances.length === 0 ? (
          <EmptyState message="No leave balances found." />
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Leave Type</th>
                <th>Allocated</th>
                <th>Used</th>
                <th>Remaining</th>
              </tr>
            </thead>
            <tbody>
              {balances.map((b) => (
                <tr key={b.id}>
                  <td>{b.employee_name}</td>
                  <td>{b.leave_type_name}</td>
                  <td>{b.allocated_days}</td>
                  <td>{b.used_days}</td>
                  <td><strong>{b.remaining_days}</strong></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
