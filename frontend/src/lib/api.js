// Minimal API client for the FastAPI backend.
// Base URL comes from VITE_API_BASE (see frontend/.env.local), default localhost:8000.

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  })
  if (!res.ok) {
    let message = `HTTP ${res.status}`
    try {
      const body = await res.json()
      if (body?.detail) message = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
    } catch {
      /* non-JSON error body */
    }
    throw new Error(message)
  }
  return res.status === 204 ? null : res.json()
}

export const api = {
  // Settings / secrets
  getSecrets: () => request('/api/settings/secrets'),
  saveSecrets: (updates) =>
    request('/api/settings/secrets', { method: 'POST', body: JSON.stringify({ updates }) }),
  testProvider: (provider) => request(`/api/settings/test/${provider}`, { method: 'POST' }),
}

export { API_BASE }
