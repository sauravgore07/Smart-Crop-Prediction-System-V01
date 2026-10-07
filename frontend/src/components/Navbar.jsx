import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Sprout, LogOut, User } from 'lucide-react'
import { useStore } from '../store/useStore'

export default function Navbar() {
  const { user, token, logout } = useStore()
  const navigate  = useNavigate()
  const location  = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const navLink = (to, label) => {
    const active = location.pathname === to
    return (
      <Link
        to={to}
        className={`relative px-3 py-5 text-sm font-medium transition-colors ${
          active ? 'text-forest' : 'text-ink-soft hover:text-ink'
        }`}
      >
        {label}
        {active && <span className="absolute left-3 right-3 bottom-0 h-[3px] bg-marigold" />}
      </Link>
    )
  }

  return (
    <nav className="bg-surface border-b border-sand px-4 sticky top-0 z-[1100]">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <Link to="/" className="flex items-center gap-2.5 py-3">
          <span className="w-8 h-8 rounded-md bg-forest flex items-center justify-center">
            <Sprout className="w-[18px] h-[18px] text-marigold" />
          </span>
          <span className="font-display text-xl font-bold text-forest tracking-tight">CropPredict</span>
        </Link>

        <div className="hidden md:flex items-center">
          {navLink('/', 'Home')}
          {navLink('/recommendations', 'Recommendations')}
          {navLink('/rotation', 'Crop rotation')}
        </div>

        <div className="flex items-center gap-2">
          {token ? (
            <>
              <span className="hidden md:flex items-center gap-1.5 text-sm text-ink-soft">
                <User className="w-4 h-4" />
                {user?.name || 'My account'}
              </span>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1 px-3 py-2 rounded-md text-sm text-ink-soft hover:bg-paper transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden md:inline">Log out</span>
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="px-3 py-2 rounded-md text-sm text-ink-soft hover:bg-paper transition-colors">
                Log in
              </Link>
              <Link to="/register" className="px-4 py-2 rounded-md text-sm bg-forest text-white hover:bg-forest-dark transition-colors font-semibold">
                Sign up
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
