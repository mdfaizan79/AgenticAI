import { AnimatePresence, motion } from 'framer-motion'
import { LANGUAGES, VOICES } from '../lib/states'

const Toggle = ({ label, hint, value, onChange }) => (
  <div className="flex items-center justify-between gap-4">
    <div><p className="text-sm font-medium">{label}</p><p className="text-xs text-slate-400">{hint}</p></div>
    <button type="button" role="switch" aria-checked={value} aria-label={label} onClick={() => onChange(!value)}
      className={`relative h-6 w-11 shrink-0 rounded-full transition ${value ? 'bg-violet-500' : 'bg-white/15'}`}>
      <span className={`absolute top-0.5 size-5 rounded-full bg-white transition-all ${value ? 'left-[22px]' : 'left-0.5'}`} />
    </button>
  </div>
)
const Select = ({ label, value, onChange, options }) => (
  <label className="block text-sm font-medium">{label}
    <select value={value} onChange={(e) => onChange(e.target.value)} className="mt-1.5 w-full rounded-xl border border-white/10 bg-[#0b0d1f] px-3 py-2.5 text-sm font-normal">
      {options.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
    </select>
  </label>
)

export default function SettingsPanel({ open, onClose, settings, update, onClear, health }) {
  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div className="fixed inset-0 z-30 bg-black/50" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose} />
          <motion.aside role="dialog" aria-modal="true" aria-label="Settings" className="glass fixed inset-y-0 right-0 z-40 w-full max-w-sm space-y-6 overflow-y-auto bg-[#080a1a]/90 p-6"
            initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }} transition={{ type: 'spring', damping: 30, stiffness: 300 }}>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Settings</h2>
              <button type="button" onClick={onClose} aria-label="Close settings" className="rounded-lg px-2 py-1 text-xl text-slate-300 hover:bg-white/10">×</button>
            </div>
            <Select label="Voice" value={settings.voice} onChange={(voice) => update({ voice })} options={VOICES.map((v) => [v, v])} />
            <Select label="Speech recognition language" value={settings.language} onChange={(language) => update({ language })} options={LANGUAGES} />
            <Toggle label="Speak replies" hint="Play Alexa's voice after each answer" value={settings.speak} onChange={(speak) => update({ speak })} />
            <Toggle label="Stop when I pause" hint="Send automatically after silence" value={settings.autoStop} onChange={(autoStop) => update({ autoStop })} />
            <button type="button" onClick={() => { onClear(); onClose() }} className="w-full rounded-xl border border-red-400/30 bg-red-500/10 py-2.5 text-sm text-red-200 hover:bg-red-500/20">Clear conversation</button>
            {health && <p className="text-xs text-slate-500">Model {health.model} · TTS {health.tts_model}</p>}
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  )
}
