import { useMemo, useState } from "react"
import { api } from "../api/client"
import { Page } from "../components/Page"
import { Card } from "../components/Card"

type Msg = { role: "user" | "assistant"; text: string }

export default function Chat() {
  const [input, setInput] = useState("")
  const [msgs, setMsgs] = useState<Msg[]>([
    { role: "assistant", text: "Hi! Ask me things like: “Show latest jobs”, “How many applications per job?”, “Find applicants for Data Analyst”." }
  ])

  async function send() {
    if (!input.trim()) return
    const u = input.trim()
    setInput("")
    setMsgs(m => [...m, { role: "user", text: u }])
    const data = await api("/chat", { method: "POST", body: JSON.stringify({ message: u }) })
    setMsgs(m => [...m, { role: "assistant", text: data.reply }])
  }

  const list = useMemo(() => msgs, [msgs])

  return (
    <Page title="Manager Assistant">
      <div className="max-w-3xl">
        <Card>
          <div className="space-y-3 max-h-[60vh] overflow-auto pr-2">
            {list.map((m, i) => (
              <div key={i} className={m.role === "user" ? "flex justify-end" : "flex justify-start"}>
                <div className={
                  "max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed " +
                  (m.role === "user" ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-900")
                }>
                  {m.text}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 flex gap-2">
            <input
              className="flex-1 rounded-xl border p-3"
              value={input}
              onChange={e=>setInput(e.target.value)}
              onKeyDown={e=> e.key === "Enter" ? send() : null}
              placeholder="Ask about jobs, applications, salaries..."
            />
            <button onClick={send} className="rounded-xl bg-blue-600 text-white px-5 font-medium hover:bg-blue-500">
              Send
            </button>
          </div>
        </Card>
      </div>
    </Page>
  )
}
