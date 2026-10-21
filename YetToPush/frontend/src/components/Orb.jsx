import { motion, useSpring, useTransform } from 'framer-motion'
import { STATES } from '../lib/states'

export default function Orb({ state, level }) {
  const c = STATES[state].color
  const smooth = useSpring(level, { stiffness: 200, damping: 18 })
  const scale = useTransform(smooth, [0, 1], [1, 1.2])
  const glow = useTransform(smooth, [0, 1], [0.5, 1])
  const thinking = state === 'thinking'
  return (
    <div role="img" aria-label={`Alexa orb: ${STATES[state].label}`} className="relative grid size-64 place-items-center sm:size-80">
      <motion.div style={{ opacity: glow, scale, background: `radial-gradient(circle, ${c}77, transparent 65%)` }} className="absolute -inset-16 rounded-full blur-2xl" />
      {[0, 1].map((i) => (
        <motion.div key={i} className="absolute inset-0 rounded-full border border-white/15"
          animate={{ scale: [1, 1.2 + i * 0.15], opacity: [0.45, 0] }}
          transition={{ duration: 3.4, repeat: Infinity, delay: i * 1.7, ease: 'easeOut' }} />
      ))}
      <motion.div style={{ scale }} className="relative size-full">
        <motion.div className="absolute inset-3 rounded-full opacity-90 blur-2xl"
          style={{ background: `conic-gradient(from 0deg, #3b82f6, #8b5cf6, ${c}, #6366f1, #3b82f6)` }}
          animate={{ rotate: thinking ? 360 : 0 }}
          transition={thinking ? { duration: 1.8, repeat: Infinity, ease: 'linear' } : { duration: 1 }} />
        <motion.div className="absolute inset-8 rounded-full"
          style={{ background: `radial-gradient(circle at 32% 26%, #fff 0%, ${c} 16%, #4f46e5 52%, #1e1b4b 100%)`, boxShadow: `inset 0 -30px 70px #0008, 0 0 90px ${c}66` }}
          animate={{ scale: state === 'idle' ? [1, 1.035, 1] : thinking ? [1, 0.96, 1] : 1 }}
          transition={{ duration: thinking ? 1.2 : 4, repeat: Infinity, ease: 'easeInOut' }} />
      </motion.div>
    </div>
  )
}
