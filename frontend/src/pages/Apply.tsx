import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { listJobs, Job } from "../api/jobs";
import { applyJob } from "../api/applications";

export default function Apply() {
  const { jobId } = useParams();
  const id = Number(jobId);
  const nav = useNavigate();

  const [job, setJob] = useState<Job | null>(null);
  const [phone, setPhone] = useState("");
  const [cover, setCover] = useState("");
  const [cv, setCv] = useState<File | null>(null);
  const [err, setErr] = useState("");
  const [ok, setOk] = useState("");

  useEffect(() => {
    (async () => {
      const jobs = await listJobs();
      setJob(jobs.find((j) => j.id === id) || null);
    })();
  }, [id]);

  return (
    <div className="card" style={{ maxWidth: 820 }}>
      <h2>Apply</h2>
      {job ? (
        <p style={{ opacity: 0.85 }}>
          You’re applying for <b>{job.role_title}</b>
        </p>
      ) : (
        <p style={{ opacity: 0.75 }}>Loading job…</p>
      )}

      <div className="grid">
        <input className="input" placeholder="Phone" value={phone} onChange={(e) => setPhone(e.target.value)} />
        <textarea rows={7} className="input" placeholder="Cover letter" value={cover} onChange={(e) => setCover(e.target.value)} />
        <input className="input" type="file" accept=".pdf,.doc,.docx" onChange={(e) => setCv(e.target.files?.[0] || null)} />

        {err && <div style={{ color: "#ffb4b4", whiteSpace: "pre-wrap" }}>{err}</div>}
        {ok && <div style={{ color: "#b7ffcc" }}>{ok}</div>}

        <button
          className="btn"
          onClick={async () => {
            setErr(""); setOk("");
            if (!cv) return setErr("Please attach your CV.");
            try {
              await applyJob({ job_id: id, phone, cover_letter: cover, cv });
              setOk("Application submitted! Check your email for confirmation.");
              setTimeout(() => nav("/jobs"), 600);
            } catch (e: any) {
              setErr(e.message);
            }
          }}
        >
          Submit application
        </button>
      </div>
    </div>
  );
}
