export function mergeChunks(chunks) {
  const out = new Float32Array(chunks.reduce((n, c) => n + c.length, 0))
  let p = 0
  for (const c of chunks) { out.set(c, p); p += c.length }
  return out
}

export function downsample(buf, inRate, outRate = 16000) {
  if (inRate <= outRate) return buf
  const ratio = inRate / outRate
  const out = new Float32Array(Math.floor(buf.length / ratio))
  for (let i = 0; i < out.length; i++) {
    const s = Math.floor(i * ratio), e = Math.min(buf.length, Math.floor((i + 1) * ratio))
    let sum = 0
    for (let j = s; j < e; j++) sum += buf[j]
    out[i] = sum / (e - s || 1)
  }
  return out
}

export function encodeWav(samples, rate = 16000) {
  const buf = new ArrayBuffer(44 + samples.length * 2)
  const v = new DataView(buf)
  const str = (o, s) => [...s].forEach((c, i) => v.setUint8(o + i, c.charCodeAt(0)))
  str(0, 'RIFF'); v.setUint32(4, 36 + samples.length * 2, true); str(8, 'WAVEfmt ')
  v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true)
  v.setUint32(24, rate, true); v.setUint32(28, rate * 2, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true)
  str(36, 'data'); v.setUint32(40, samples.length * 2, true)
  samples.forEach((x, i) => {
    const s = Math.max(-1, Math.min(1, x))
    v.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true)
  })
  return buf
}
