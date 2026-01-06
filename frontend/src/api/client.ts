import { getToken } from "../auth"

export const API_BASE = "http://127.0.0.1:8000"

export async function api(path: string, init: RequestInit = {}) {
  const token = getToken()
  const headers = new Headers(init.headers || {})
  headers.set("Content-Type", "application/json")
  if (token) headers.set("Authorization", `Bearer ${token}`)

  const res = await fetch(`${API_BASE}${path}`, { ...init, headers })
  if (!res.ok) {
    const txt = await res.text()
    throw new Error(txt || `HTTP ${res.status}`)
  }
  return res.json()
}
