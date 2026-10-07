import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Sprout } from 'lucide-react'
import { register, getMe } from '../services/api'
import { useStore } from '../store/useStore'

export default function Register() {
  const navigate = useNavigate()
  const setAuth  = useStore(s => s.setAuth)

  const [form,    setForm]    = useState({ name: '', email: '', password: '', confirm: '' })
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    if (form.password !== form.confirm) { setError('Passwords do not match'); return }
    setLoading(true)
    setError('')
    try {
      const res   = await register({ name: form.name, email: form.email, password: form.password })
      const token = res.data.access_token
      const me    = await getMe()
      setAuth(me.data, token)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  const field = (id, label, type, placeholder) => (
    <div>
      <label className="block text-sm font-medium mb-1 text-ink">{label}</label>
      <input
        type={type} required
        value={form[id]}
        onChange={e => setForm(f => ({ ...f, [id]: e.target.value }))}
        className="w-full px-4 py-2.5 border border-sand rounded-xl focus:ring-2 focus:ring-primary/40 focus:border-primary outline-none bg-white"
        placeholder={placeholder}
      />
    </div>
  )

  return (
    <div className="max-w-md mx-auto mt-12">
      <div className="bg-surface rounded-2xl border border-sand p-8">
        <div className="flex items-center gap-2.5 mb-6">
          <span className="w-8 h-8 rounded-md bg-forest flex items-center justify-center">
            <Sprout className="w-[18px] h-[18px] text-marigold" />
          </span>
          <span className="font-display text-xl font-semibold text-forest">CropPredict</span>
        </div>

        <h2 className="font-display text-2xl font-semibold mb-1 text-ink">Create account</h2>
        <p className="text-ink-soft text-sm mb-6">Save your farms and track recommendations.</p>

        {error && (
          <div className="bg-clay-soft border border-clay/30 text-clay rounded-xl px-4 py-3 text-sm mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {field('name',    'Full name', 'text',     'Your name')}
          {field('email',   'Email',     'email',    'you@example.com')}
          {field('password','Password',  'password', '8+ characters')}
          {field('confirm', 'Confirm password', 'password', '••••••••')}
          <button
            type="submit" disabled={loading}
            className="w-full py-3 bg-forest text-white rounded-xl font-semibold hover:bg-forest-dark transition-colors disabled:opacity-60"
          >
            {loading ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <p className="text-sm text-center text-ink-soft mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-primary font-medium hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
