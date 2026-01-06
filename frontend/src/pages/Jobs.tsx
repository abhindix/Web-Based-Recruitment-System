import { useEffect, useState } from "react";
import { listJobs, Job } from "../api/jobs";
import { Link } from "react-router-dom";
const role = localStorage.getItem("role");

export default function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        setJobs(await listJobs());
      } catch (e: any) {
        setErr(e.message);
      }
    })();
  }, []);

  return (
    <div className="grid">
      <div className="card">
        <h2>Open roles</h2>
        <p style={{ opacity: 0.8 }}>Browse roles and apply in a few clicks.</p>
        {err && <div style={{ color: "#ffb4b4" }}>{err}</div>}
      </div>

      <div className="grid2">
        {jobs.map((j) => (
          <div className="card" key={j.id}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
              <div>
                <div style={{ fontSize: 18, fontWeight: 800 }}>{j.role_title}</div>
                <div style={{ opacity: 0.8, marginTop: 6, whiteSpace: "pre-wrap" }}>{j.requirements}</div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div className="badge">Job #{j.id}</div>
                <div style={{ marginTop: 8, opacity: 0.9 }}>
                  {j.indicative_salary ? `₹${j.indicative_salary.toLocaleString()} / yr` : "Salary: TBD"}
                </div>
              </div>
            </div>

            <hr />
            {role === "applicant" && <Link className="btn" to={`/apply/${j.id}`}>Apply</Link>}
          </div>
        ))}
      </div>
    </div>
  );
}
