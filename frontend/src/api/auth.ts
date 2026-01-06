import { api } from "./client";

export async function register(payload: { email: string; full_name: string; password: string; role: "manager" | "applicant" }) {
  return api("/auth/register", { method: "POST", body: JSON.stringify(payload) });
}

export async function login(email: string, password: string) {
  // OAuth2PasswordRequestForm requires x-www-form-urlencoded:
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  const res = await fetch("http://localhost:8000/auth/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  if (!res.ok) {
    throw new Error("Invalid credentials")
  }
  
  const data = await res.json()

  // 🔐 Store token
  localStorage.setItem("token", data.access_token)
  localStorage.setItem("role", data.role)

  return data
}
