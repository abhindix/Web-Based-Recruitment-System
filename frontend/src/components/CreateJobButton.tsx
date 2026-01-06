import { getUser } from "../auth"

export default function CreateJobButton() {
  const user = getUser()

  if (!user || !["admin", "manager"].includes(user.role)) {
    return null
  }

  return (
    <button className="btn-primary">
      Create Job
    </button>
  )
}
