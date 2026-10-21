import { useEffect, useRef } from 'react'
import { STATES } from '../lib/states'

export default function Waveform({ freq, state }) {
  const ref = useRef(null)
  const color = useRef(STATES[state].color)
  color.current = STATES[state].color
  useEffect(() => {
    const cv = ref.current, g = cv.getContext('2d')
    const fit = () => { const d = window.devicePixelRatio || 1; cv.width = cv.clientWidth * d; cv.height = cv.clientHeight * d }
    fit()
    const ro = new ResizeObserver(fit); ro.observe(cv)
    let raf
    const draw = () => {
      const { width: w, height: h } = cv, f = freq.current, N = 48, step = w / N
      g.clearRect(0, 0, w, h); g.fillStyle = color.current
      for (let k = 0; k < N; k++) {
        const bin = Math.floor((Math.abs(k - N / 2) / (N / 2)) * f.length * 0.7)
        const bh = Math.max(3, (f[bin] / 255) * h * 0.95)
        g.globalAlpha = 0.35 + (f[bin] / 255) * 0.65
        g.beginPath(); g.roundRect(k * step + step * 0.2, (h - bh) / 2, step * 0.6, bh, step * 0.3); g.fill()
      }
      raf = requestAnimationFrame(draw)
    }
    draw()
    return () => { cancelAnimationFrame(raf); ro.disconnect() }
  }, [freq])
  return <canvas ref={ref} aria-hidden="true" className="h-14 w-full max-w-md" />
}
