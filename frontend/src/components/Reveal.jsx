import { useEffect, useRef, useState } from 'react'

// Fades/slides children in once they scroll into view.
export default function Reveal({ children, index = 0, className = '' }) {
  const ref = useRef(null)
  const [shown, setShown] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el || !('IntersectionObserver' in window)) { setShown(true); return }
    const io = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) { setShown(true); io.disconnect() }
    }, { threshold: 0.15 })
    io.observe(el)
    return () => io.disconnect()
  }, [])

  return (
    <div ref={ref} style={{ '--i': index }} className={`reveal ${shown ? 'in' : ''} ${className}`}>
      {children}
    </div>
  )
}
