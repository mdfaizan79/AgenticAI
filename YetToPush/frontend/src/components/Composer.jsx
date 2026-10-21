import { useState } from 'react'
import { PROMPTS } from '../lib/states'

export default function Composer({ onSend, disabled }) {
  const [v, setV] = useState('')
  const submit = (e) => { e.preventDefault(); if (!v.trim() || disabled) return; onSend(v); setV('') }
  return (
    <div className="border-t border-white/10 p-3">
      <div className="mb-3 flex gap-2 overflow-x-auto pb-1" role="group" aria-label="Quick prompts">
        {PROMPTS.map((p) => <button key={p} type="button" className="chip" disabled={disabled} onClick={() => onSend(p)}>{p}</button>)}
      </div>
      <form onSubmit={submit} className="flex gap-2">
        <input value={v} onChange={(e) => setV(e.target.value)} aria-label="Message Alexa" placeholder="Type a message…" maxLength={2000}
          className="min-w-0 flex-1 rounded-xl border border-white/10 bg-black/30 px-4 py-2.5 text-sm placeholder:text-slate-500 focus:border-violet-400/60" />
        <button type="submit" disabled={disabled || !v.trim()} className="rounded-xl bg-gradient-to-br from-blue-500 to-violet-600 px-5 text-sm font-medium text-white transition disabled:opacity-40">Send</button>
      </form>
    </div>
  )
}
