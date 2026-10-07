import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Sprout } from 'lucide-react'
import { login, getMe } from '../services/api'
import { useStore } from '../store/useStore'

export default function Login() {
  const navigate = useNavigate()
  const setAuth  = useStore(s => s.setAuth)

  const [form,    setForm]    = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res  = await login(form)
      const token = res.data.access_token
      localStorage.setItem('token', token)
      const me   = await getMe()
      setAuth(me.data, token)
      navigate('/')
    } catch (err) {
      localStorage.removeItem('token')
      setError(err.response?.data?.detail || 'Login failed. Check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto mt-12">
      <div className="bg-surface rounded-2xl border border-sand p-8">
        <div className="flex items-center gap-2.5 mb-6">
          <span className="w-8 h-8 rounded-md bg-forest flex items-center justify-center">
            <Sprout className="w-[18px] h-[18px] text-marigold" />
          </span>
          <span className="font-display text-xl font-semibold text-forest">CropPredict</span>
        </div>

        <h2 className="font-display text-2xl font-semibold mb-1 text-ink">Welcome back</h2>
        <p className="text-ink-soft text-sm mb-6">Sign in to access your saved farms.</p>

        {error && (
          <div className="bg-clay-soft border border-clay/30 text-clay rounded-xl px-4 py-3 text-sm mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1 text-ink">Email</label>
            <input
              type="email" required
              value={form.email}
              onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
              className="w-full px-4 py-2.5 border border-sand rounded-xl focus:ring-2 focus:ring-primary/40 focus:border-primary outline-none bg-white"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-ink">Password</label>
            <input
              type="password" required
              value={form.password}
              onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
              className="w-full px-4 py-2.5 border border-sand rounded-xl focus:ring-2 focus:ring-primary/40 focus:border-primary outline-none bg-white"
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit" disabled={loading}
            className="w-full py-3 bg-forest text-white rounded-xl font-semibold hover:bg-forest-dark transition-colors disabled:opacity-60"
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p className="text-sm text-center text-ink-soft mt-6">
          Don't have an account?{' '}
          <Link to="/register" className="text-primary font-medium hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  )
}
