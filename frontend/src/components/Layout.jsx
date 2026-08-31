import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navLinkClass = ({ isActive }) => `nav-link${isActive ? ' active' : ''}`

  return (
    <>
      <nav className="navbar">
        <div className="navbar-inner">
          <NavLink to="/dashboard" className="brand">
            Leave &amp; Attendance
          </NavLink>
          <div className="nav-links">
            <NavLink to="/dashboard" className={navLinkClass}>
              Dashboard
            </NavLink>
            <NavLink to="/attendance" className={navLinkClass}>
              Attendance
            </NavLink>
            <NavLink to="/leaves" className={navLinkClass}>
              Leave Requests
            </NavLink>
            <NavLink to="/balances" className={navLinkClass}>
              Balances
            </NavLink>
            <NavLink to="/departments" className={navLinkClass}>
              Departments
            </NavLink>
            {(user?.role === 'admin' || user?.role === 'manager') && (
              <NavLink to="/users" className={navLinkClass}>
                Users
              </NavLink>
            )}
            <NavLink to="/profile" className={navLinkClass}>
              Profile
            </NavLink>
            <button className="btn btn-outline" onClick={handleLogout} style={{ marginLeft: 8 }}>
              Logout
            </button>
          </div>
        </div>
      </nav>
      <Outlet />
    </>
  )
}
