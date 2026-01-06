const KEY = "token"

export function setToken(t: string) { localStorage.setItem(KEY, t) }
export function getToken() { return localStorage.getItem(KEY) }
export function clearToken() { localStorage.removeItem(KEY); localStorage.removeItem("role"); }
export function getUser() {
  const token = localStorage.getItem("token")
  if (!token) return null
  return JSON.parse(atob(token.split(".")[1]))
}