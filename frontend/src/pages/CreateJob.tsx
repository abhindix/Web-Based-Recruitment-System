import { useState } from "react"
import { api } from "../api/client"
import { Page } from "../components/Page"
import { Card } from "../components/Card"

export default function CreateJob() {
  const [title, setTitle] = useState("")
  const [requirements, setReq] = useState("")
  const [salary, setSalary] = useState("")
  const [msg, setMsg] = useState<string | null>(null)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setMsg(null)
    const payload = {
      role_title: title,
      requirements,
      indicative_salary: salary ? parseInt(salary, 10) : null
    };
    await api("/jobs", { method: "POST", body: JSON.stringify(payload) })
    setTitle(""); setReq(""); setSalary("")
    setMsg("Job created ✅")
  }

  return (
    <Page title="Create a Job">
      <div className="max-w-2xl">
        <Card>
          <form className="space-y-4" onSubmit={submit}>
            <div>
              <label className="text-sm font-medium">Role title</label>
              <input className="mt-1 w-full rounded-xl border p-3" value={title} onChange={e=>setTitle(e.target.value)} />
            </div>
            <div>
              <label className="text-sm font-medium">Requirements</label>
              <textarea className="mt-1 w-full rounded-xl border p-3 min-h-[140px]" value={requirements} onChange={e=>setReq(e.target.value)} />
            </div>
            <div>
              <label className="text-sm font-medium">Indicative salary</label>
              <input className="mt-1 w-full rounded-xl border p-3" value={salary} onChange={e=>setSalary(e.target.value)} />
            </div>
            {msg && <p className="text-sm text-emerald-700">{msg}</p>}
            <button className="rounded-xl bg-emerald-600 text-white px-5 py-3 font-medium hover:bg-emerald-500">
              Publish job
            </button>
          </form>
        </Card>
      </div>
    </Page>
  )
}
