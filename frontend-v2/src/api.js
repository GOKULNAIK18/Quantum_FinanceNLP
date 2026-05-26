const BASE = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? '/api' : 'https://quantumfinancenlp-production.up.railway.app')

export async function analyzeTicket(ticker) {
  const res = await fetch(`${BASE}/analyze/${encodeURIComponent(ticker)}`)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || res.statusText)
  }
  return res.json()
}
