import { Navigate } from 'react-router-dom'
import { useStore } from '../store/useStore'

/**
 * Wraps a page that requires login.
 * Usage: <AuthGuard><MySavedFarms /></AuthGuard>
 */
export default function AuthGuard({ children }) {
  const token = useStore(s => s.token)
  if (!token) return <Navigate to="/login" replace />
  return children
}
