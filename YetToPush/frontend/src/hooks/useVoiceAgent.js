import { useCallback, useEffect, useRef, useState } from 'react'
import { useMotionValue } from 'framer-motion'
import { downsample, encodeWav, mergeChunks } from '../lib/audio'

const load = (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d } catch { return d } }
const save = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)) } catch { /* storage unavailable */ } }
const sid = (() => {
  let s = load('alexa-session', null)
  if (!s) { s = Math.random().toString(36).slice(2) + Date.now().toString(36); save('alexa-session', s) }
  return s
})()
const DEFAULTS = { voice: 'coral', language: 'en-IN', speak: true, autoStop: true }

export default function useVoiceAgent() {
  const [state, setStateRaw] = useState('idle')
  const [messages, setMessages] = useState(() => load('alexa-messages', []))
  const [error, setError] = useState(null)
  const [connected, setConnected] = useState(false)
  const [health, setHealth] = useState(null)
  const [settings, setSettings] = useState(() => ({ ...DEFAULTS, ...load('alexa-settings', {}) }))

  const level = useMotionValue(0)            // 0..1 live audio level (mic or AI voice)
  const freq = useRef(new Uint8Array(64))    // live frequency data for the waveform
  const ws = useRef(null), ctx = useRef(null), micAn = useRef(null), outAn = useRef(null), active = useRef(null)
  const rec = useRef(null), playing = useRef(null), finishRef = useRef(() => {})
  const stateRef = useRef('idle'), settingsRef = useRef(settings), idRef = useRef(Date.now())

  const setState = (s) => { stateRef.current = s; setStateRaw(s) }
  const fail = (msg) => { setError(msg); setState('error') }
  const addMsg = (m) => setMessages((p) => [...p, { id: idRef.current++, ...m }].slice(-100))

  useEffect(() => { save('alexa-messages', messages) }, [messages])
  useEffect(() => { fetch('/api/health').then((r) => r.json()).then(setHealth).catch(() => setHealth(null)) }, [])
  useEffect(() => {
    if (state !== 'error') return
    const t = setTimeout(() => stateRef.current === 'error' && setState('idle'), 6000)
    return () => clearTimeout(t)
  }, [state])

  const send = (obj) => ws.current?.readyState === 1 && ws.current.send(JSON.stringify(obj))

  const getCtx = () => {
    if (!ctx.current) {
      const c = new (window.AudioContext || window.webkitAudioContext)()
      micAn.current = c.createAnalyser(); outAn.current = c.createAnalyser()
      micAn.current.fftSize = outAn.current.fftSize = 128
      micAn.current.smoothingTimeConstant = outAn.current.smoothingTimeConstant = 0.7
      outAn.current.connect(c.destination)   // only the AI voice is routed to speakers
      ctx.current = c
    }
    if (ctx.current.state === 'suspended') ctx.current.resume()
    return ctx.current
  }

  const stopSpeaking = () => {
    const s = playing.current
    if (!s) return
    playing.current = null
    s.onended = null
    try { s.stop() } catch { /* already stopped */ }
    active.current = null
  }

  const playAudio = async (buf) => {
    try {
      const c = getCtx()
      const audio = await c.decodeAudioData(buf)
      const src = c.createBufferSource()
      src.buffer = audio
      src.connect(outAn.current)
      src.onended = () => { if (playing.current === src) { playing.current = null; active.current = null; setState('idle') } }
      stopSpeaking()
      playing.current = src; active.current = outAn.current
      setState('speaking')
      src.start()
    } catch { fail('Could not play the voice reply. Check your browser audio settings.') }
  }

  // WebSocket connection with auto-reconnect
  useEffect(() => {
    let closed = false, timer
    const open = () => {
      const sock = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws?session=${sid}`)
      sock.binaryType = 'arraybuffer'
      ws.current = sock
      sock.onopen = () => { setConnected(true); sock.send(JSON.stringify({ type: 'config', ...settingsRef.current })) }
      sock.onclose = () => { setConnected(false); if (!closed) timer = setTimeout(open, 2000) }
      sock.onmessage = (e) => {
        if (e.data instanceof ArrayBuffer) return playAudio(e.data)
        const m = JSON.parse(e.data)
        if (m.type === 'state') setState(m.state)
        else if (m.type === 'user') addMsg({ role: 'user', text: m.text })
        else if (m.type === 'assistant') addMsg({ role: 'assistant', text: m.text })
        else if (m.type === 'tool') addMsg({ role: 'tool', name: m.name, text: m.result })
        else if (m.type === 'cleared') setMessages([])
        else if (m.type === 'error') fail(m.message)
      }
    }
    open()
    return () => { closed = true; clearTimeout(timer); ws.current?.close() }
  }, [])

  const startListening = async () => {
    if (!connected) return fail('Not connected to the Alexa backend. Is the server running on port 8000?')
    stopSpeaking()
    const c = getCtx()
    let stream
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, channelCount: 1 } })
    } catch (e) {
      return fail(e.name === 'NotAllowedError' ? 'Microphone permission was denied. Allow it in your browser settings.' : 'No microphone available.')
    }
    const source = c.createMediaStreamSource(stream)
    const node = c.createScriptProcessor(4096, 1, 1)
    const chunks = []
    node.onaudioprocess = (e) => chunks.push(new Float32Array(e.inputBuffer.getChannelData(0)))
    source.connect(micAn.current); source.connect(node); node.connect(c.destination)
    active.current = micAn.current
    rec.current = { stream, source, node, chunks, start: performance.now(), heard: false, last: 0 }
    setError(null); setState('listening')
  }

  finishRef.current = () => {
    const r = rec.current
    if (!r) return
    rec.current = null; active.current = null
    r.node.disconnect(); r.source.disconnect(); r.stream.getTracks().forEach((t) => t.stop())
    if (!r.heard) return fail('No speech detected. Try again.')
    const pcm = downsample(mergeChunks(r.chunks), ctx.current.sampleRate)
    ws.current.send(encodeWav(pcm))
    setState('thinking')
  }

  // Drives the orb + waveform from real analyser data; also ends recording on silence
  useEffect(() => {
    if (state !== 'listening' && state !== 'speaking') { freq.current.fill(0); level.set(0); return }
    let raf
    const tick = () => {
      const an = active.current
      if (an) {
        an.getByteFrequencyData(freq.current)
        let sum = 0
        for (let i = 0; i < freq.current.length; i++) sum += freq.current[i]
        const lv = Math.min(1, (sum / freq.current.length / 255) * 2.4)
        level.set(lv)
        const r = rec.current
        if (r) {
          const now = performance.now()
          if (lv > 0.12) { r.heard = true; r.last = now }
          if ((settingsRef.current.autoStop && r.heard && now - r.last > 1400) || (!r.heard && now - r.start > 8000) || now - r.start > 20000) finishRef.current()
        }
      }
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [state, level])

  const toggleMic = useCallback(() => {
    if (stateRef.current === 'listening') finishRef.current()
    else if (stateRef.current !== 'thinking') startListening()
  }, [connected]) // eslint-disable-line react-hooks/exhaustive-deps

  const sendText = (text) => {
    if (!text.trim() || !connected || stateRef.current === 'thinking') return
    stopSpeaking(); getCtx(); setError(null)
    send({ type: 'text', text })
    setState('thinking')
  }

  const updateSettings = (patch) => {
    const next = { ...settings, ...patch }
    settingsRef.current = next; setSettings(next); save('alexa-settings', next)
    send({ type: 'config', ...next })
  }

  const clear = () => { send({ type: 'clear' }); setMessages([]) }
  const dismissError = () => { setError(null); if (stateRef.current === 'error') setState('idle') }

  return { state, messages, error, connected, health, settings, level, freq, toggleMic, sendText, updateSettings, clear, dismissError }
}
