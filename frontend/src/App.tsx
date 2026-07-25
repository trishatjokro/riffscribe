import { useState } from "react";
import { uploadAudio, pollJob, JobResult } from "./api";

// v1 UI: upload a clip -> poll the job -> show the resulting tab.
// The TabViewer (alphaTab) render + synced playback is a P1 upgrade over the
// plain ASCII preview shown here.
export default function App() {
  const [job, setJob] = useState<JobResult | null>(null);
  const [busy, setBusy] = useState(false);

  async function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    setJob(null);
    try {
      const jobId = await uploadAudio(file);
      // Poll until the pipeline finishes.
      let result = await pollJob(jobId);
      while (result.status === "queued" || result.status === "processing") {
        await new Promise((r) => setTimeout(r, 1000));
        result = await pollJob(jobId);
      }
      setJob(result);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main style={{ maxWidth: 720, margin: "3rem auto", fontFamily: "system-ui" }}>
      <h1>🎸 riffscribe</h1>
      <p>Upload a guitar clip and get a first-draft tab you can fix in seconds.</p>

      <input type="file" accept="audio/*" onChange={onFile} disabled={busy} />
      {busy && <p>Transcribing…</p>}

      {job?.status === "error" && <p style={{ color: "crimson" }}>Error: {job.error}</p>}
      {job?.status === "done" && (
        <>
          <p style={{ color: "#888", fontSize: ".85rem" }}>
            {String(job.meta.num_notes ?? "?")} notes
            {job.meta.tempo_bpm ? ` · ~${Math.round(Number(job.meta.tempo_bpm))} bpm` : ""}
          </p>
          <pre style={{ background: "#111", color: "#eee", padding: "1rem", overflowX: "auto" }}>
            {job.ascii_tab}
          </pre>
        </>
      )}
    </main>
  );
}
