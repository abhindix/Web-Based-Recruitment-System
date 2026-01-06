import { api } from "./client";

export type Job = { id: number; role_title: string; requirements: string; indicative_salary?: number | null; hiring_manager_id: number };

export function listJobs() {
  return api<Job[]>("/jobs");
}

export async function createJob(payload: any) {
  const token = localStorage.getItem("token");

  const res = await fetch("http://localhost:8000/jobs", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to create job");
  }

  return res.json();
}