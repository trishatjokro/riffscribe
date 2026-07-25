"""riffscribe HTTP API (FastAPI).

Transcription can take seconds to minutes, so uploads create a *job* that the
frontend polls. v1 runs the pipeline inline in a background task; a real queue
(e.g. Redis/RQ or Celery) is a P1 concern once concurrency matters.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from tempfile import gettempdir

from fastapi import BackgroundTasks, FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from . import __version__

app = FastAPI(title="riffscribe", version=__version__)

_STATIC = Path(__file__).parent / "static"

# Dev CORS: the Vite frontend runs on a different port.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_UPLOAD_DIR = Path(gettempdir()) / "riffscribe_uploads"
_UPLOAD_DIR.mkdir(exist_ok=True)


class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    done = "done"
    error = "error"


@dataclass
class Job:
    id: str
    status: JobStatus = JobStatus.queued
    ascii_tab: str | None = None
    tab: dict | None = None          # structured tab for the interactive viewer
    error: str | None = None
    meta: dict = field(default_factory=dict)


# In-memory job store — fine for a single-process dev server; swap for a real
# store when we add a worker queue (P1).
_JOBS: dict[str, Job] = {}


def _run_pipeline(job_id: str, audio_path: Path) -> None:
    """Execute the transcription pipeline for a job and record the result."""
    from .pipeline.transcribe import transcribe
    from .pipeline.tab import assign_tab
    from .pipeline.export import to_ascii

    job = _JOBS[job_id]
    job.status = JobStatus.processing
    try:
        events = transcribe(audio_path)          # audio -> notes  (P0: not yet impl)
        tab = assign_tab(events)                  # notes -> string/fret (implemented)
        job.ascii_tab = to_ascii(tab)
        job.meta = {"tempo_bpm": tab.tempo_bpm, "num_notes": len(tab.notes)}
        job.status = JobStatus.done
    except NotImplementedError as exc:
        job.status = JobStatus.error
        job.error = f"pipeline stage not implemented: {exc}"
    except Exception as exc:  # noqa: BLE001 - surface any failure to the client
        job.status = JobStatus.error
        job.error = str(exc)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


@app.post("/transcribe")
async def create_job(file: UploadFile, background: BackgroundTasks) -> dict:
    """Accept an audio upload and kick off transcription; returns a job id."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="no file provided")

    job_id = uuid.uuid4().hex
    dest = _UPLOAD_DIR / f"{job_id}_{file.filename}"
    dest.write_bytes(await file.read())

    _JOBS[job_id] = Job(id=job_id)
    background.add_task(_run_pipeline, job_id, dest)
    return {"job_id": job_id, "status": JobStatus.queued}


@app.get("/job/{job_id}")
def get_job(job_id: str) -> dict:
    """Poll a job's status and (when done) its resulting tab."""
    job = _JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return {
        "job_id": job.id,
        "status": job.status,
        "ascii_tab": job.ascii_tab,
        "error": job.error,
        "meta": job.meta,
    }
