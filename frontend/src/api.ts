// Thin client for the riffscribe backend.
const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type JobStatus = "queued" | "processing" | "done" | "error";

export interface JobResult {
  job_id: string;
  status: JobStatus;
  ascii_tab: string | null;
  error: string | null;
  meta: Record<string, unknown>;
}

export async function uploadAudio(file: File): Promise<string> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/transcribe`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`upload failed: ${res.status}`);
  const { job_id } = await res.json();
  return job_id;
}

export async function pollJob(jobId: string): Promise<JobResult> {
  const res = await fetch(`${BASE}/job/${jobId}`);
  if (!res.ok) throw new Error(`poll failed: ${res.status}`);
  return res.json();
}
