import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'

export default function Transcript({ messages, thinking }) {
  const end = useRef(null)
  useEffect(() => { end.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }) }, [messages, thinking])
  return (
    <div role="log" aria-live="polite" aria-label="Conversation transcript" className="flex-1 space-y-3 overflow-y-auto p-4">
      {!messages.length && (
        <p className="grid h-full place-items-center text-center text-sm text-slate-400">
          Say something or pick a quick prompt below.<br />Your conversation appears here.
        </p>
      )}
      {messages.map((m) => m.role === 'tool' ? (
        <div key={m.id} className="mx-auto w-fit max-w-full truncate rounded-full border border-violet-400/20 bg-violet-500/10 px-3 py-1 text-xs text-violet-200" title={m.text}>
          Tool {m.name}: {m.text}
        </div>
      ) : (
        <motion.div key={m.id} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
          className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
          <p className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${m.role === 'user' ? 'rounded-br-md bg-gradient-to-br from-blue-500/80 to-violet-600/80 text-white' : 'rounded-bl-md border border-white/10 bg-white/5 text-slate-100'}`}>
            <span className="sr-only">{m.role === 'user' ? 'You: ' : 'Alexa: '}</span>{m.text}
          </p>
        </motion.div>
      ))}
      {thinking && <p className="text-xs text-violet-300">Alexa is thinking…</p>}
      <div ref={end} />
    </div>
  )
}
