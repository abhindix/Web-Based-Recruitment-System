export async function applyJob(payload: { job_id: number; phone: string; cover_letter: string; cv: File }) {
  const fd = new FormData();
  fd.append("cv", payload.cv);
  fd.append("body", new Blob([JSON.stringify({
    job_id: payload.job_id,
    phone: payload.phone,
    cover_letter: payload.cover_letter,
  })], { type: "application/json" }));

  // FastAPI with mixed JSON+file: easiest is send fields separately
  // We'll send as form fields:
  const fd2 = new FormData();
  fd2.append("cv", payload.cv);
  fd2.append("job_id", String(payload.job_id));
  fd2.append("phone", payload.phone);
  fd2.append("cover_letter", payload.cover_letter);

  const token = localStorage.getItem("token");
  const res = await fetch("http://localhost:8000/applications", {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    body: fd2,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
