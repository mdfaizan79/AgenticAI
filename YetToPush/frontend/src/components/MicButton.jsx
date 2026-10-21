import { motion } from 'framer-motion'

export default function MicButton({ state, onClick }) {
  const on = state === 'listening'
  return (
    <div className="relative grid place-items-center">
      {on && [0, 1].map((i) => (
        <motion.span key={i} className="absolute size-24 rounded-full border border-cyan-300/60"
          animate={{ scale: [1, 1.9], opacity: [0.6, 0] }} transition={{ duration: 1.6, repeat: Infinity, delay: i * 0.8 }} />
      ))}
      <motion.button type="button" onClick={onClick} disabled={state === 'thinking'}
        whileHover={{ scale: 1.06 }} whileTap={{ scale: 0.94 }} aria-pressed={on}
        aria-label={on ? 'Stop listening and send' : 'Start listening'}
        className={`relative grid size-24 place-items-center rounded-full text-white shadow-[0_0_50px_-8px] transition-colors disabled:opacity-40 ${on ? 'bg-gradient-to-br from-cyan-400 to-blue-600 shadow-cyan-400' : 'bg-gradient-to-br from-blue-500 to-violet-600 shadow-violet-500'}`}>
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          {on ? <rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor" /> : <><rect x="9" y="2" width="6" height="12" rx="3" /><path d="M5 11a7 7 0 0 0 14 0M12 18v4" /></>}
        </svg>
      </motion.button>
    </div>
  )
}
