"use client"

import { useEffect, useState } from "react"

type AuthMode = "login" | "register"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000"
const AFTER_LOGIN = process.env.NEXT_PUBLIC_AFTER_LOGIN_URL ?? `${API_BASE}/`

export default function AuthPage() {
  const [mode, setMode] = useState<AuthMode>("login")
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [email, setEmail] = useState("")
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    const saved = localStorage.getItem("authToken")
    if (saved) setToken(saved)
  }, [])

  const resetMessages = () => setMessage(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    resetMessages()
    setLoading(true)
    try {
      if (mode === "register") {
        const res = await fetch(`${API_BASE}/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password, email: email || undefined }),
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.detail || "Failed to register")
        localStorage.setItem("authToken", data.access_token)
        setToken(data.access_token)
        setMessage("Registered and logged in.")
        // Redirect to landing page after successful registration
        window.location.href = AFTER_LOGIN
      } else {
        const form = new URLSearchParams()
        form.append("username", username)
        form.append("password", password)
        const res = await fetch(`${API_BASE}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: form.toString(),
              mode: "cors",
            })
        const data = await res.json()
        if (!res.ok) throw new Error(data.detail || "Failed to login")
        localStorage.setItem("authToken", data.access_token)
        setToken(data.access_token)
        setMessage("Logged in.")
        // Redirect to landing page after successful login
        window.location.href = AFTER_LOGIN
      }
    } catch (err: any) {
      setMessage(err.message || "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  async function fetchProfile() {
    resetMessages()
    if (!token) {
      setMessage("No token saved")
      return
    }
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
          mode: "cors",
        })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || "Failed to fetch profile")
      setMessage(`Hello ${data.username} (${data.email ?? "no email"})`)
    } catch (err: any) {
      setMessage(err.message || "Something went wrong")
    }
  }

  function logout() {
    localStorage.removeItem("authToken")
    setToken(null)
    setMessage("Logged out")
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white px-4">
      <div className="w-full max-w-md space-y-6 bg-slate-800/70 border border-slate-700 rounded-xl p-8 shadow-xl">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">F1-Score Grand Prix Auth</h1>
          <div className="flex gap-2 text-sm">
            <button
              className={`px-3 py-1 rounded ${mode === "login" ? "bg-indigo-500" : "bg-slate-700"}`}
              onClick={() => setMode("login")}
            >
              Login
            </button>
            <button
              className={`px-3 py-1 rounded ${mode === "register" ? "bg-indigo-500" : "bg-slate-700"}`}
              onClick={() => setMode("register")}
            >
              Register
            </button>
          </div>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <label className="text-sm text-slate-200">Username</label>
            <input
              className="w-full rounded border border-slate-700 bg-slate-900 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          {mode === "register" && (
            <div className="space-y-2">
              <label className="text-sm text-slate-200">Email (optional)</label>
              <input
                className="w-full rounded border border-slate-700 bg-slate-900 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                type="email"
              />
            </div>
          )}
          <div className="space-y-2">
            <label className="text-sm text-slate-200">Password</label>
            <input
              className="w-full rounded border border-slate-700 bg-slate-900 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-indigo-500 hover:bg-indigo-600 transition text-white rounded px-4 py-2 font-medium"
            disabled={loading}
          >
            {loading ? "Please wait..." : mode === "login" ? "Login" : "Register"}
          </button>
        </form>

        <div className="flex items-center justify-between text-sm text-slate-300">
          <span>Token saved: {token ? "yes" : "no"}</span>
          <div className="flex gap-2">
            <button className="px-3 py-1 rounded bg-slate-700" onClick={fetchProfile}>Check profile</button>
            <button className="px-3 py-1 rounded bg-slate-700" onClick={logout}>Logout</button>
          </div>
        </div>

        {message && (
          <div className="text-sm text-slate-100 bg-slate-700/60 border border-slate-600 rounded p-3">
            {message}
          </div>
        )}

        <div className="text-xs text-slate-400 space-y-1">
          <p>Backend base: {API_BASE}</p>
          <p>Set NEXT_PUBLIC_API_BASE in env to point to your API.</p>
        </div>
      </div>
    </div>
  )
}