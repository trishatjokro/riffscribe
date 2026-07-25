# riffscribe backend

The audio → guitar tab engine, plus a FastAPI wrapper.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Optional extras:

```bash
pip install -e ".[mono]"        # CREPE, for cleaner monophonic pitch
pip install -e ".[separation]"  # Demucs, for full-mix guitar isolation (P2)
```

## Run the API

```bash
uvicorn app.main:app --reload    # http://localhost:8000  (docs at /docs)
```

## Run the CLI

```bash
riffscribe path/to/riff.wav
```

## Pipeline (`app/pipeline/`)

| Stage | Module | Status |
|---|---|---|
| Source separation (optional) | `separate.py` | stub (P2) |
| Audio → notes | `transcribe.py` | **implemented** (Basic Pitch → monophonic) |
| Notes → string+fret | `tab.py` | **implemented** (DP fret optimizer) |
| Export (ASCII / .gp5 / MusicXML) | `export.py` | ASCII done; .gp5/MusicXML stub (P0) |

## End-to-end: transcribe real audio

The transcription stage needs the ML runtime, which is **not** installed by the
light dev install. Add it:

```bash
pip install basic-pitch
# Apple Silicon: a lighter runtime avoids full TensorFlow —
#   pip install "basic-pitch[coreml]"   # or  "basic-pitch[onnx]"
```

Then transcribe a clip end-to-end (audio → notes → tab):

```bash
riffscribe path/to/riff.wav          # prints ASCII tab
# or via the API:
uvicorn app.main:app --reload
curl -F "file=@path/to/riff.wav" localhost:8000/transcribe   # -> {"job_id": ...}
curl localhost:8000/job/<job_id>                             # poll for the tab
```

The first run downloads the Basic Pitch model (~a few MB) and is slow to warm up.
Use a clean, mostly-solo guitar clip — accuracy drops on distortion and full mixes
(see `docs/architecture.md`).

## Tests

```bash
pytest
```

The fret-optimizer tests (`tests/test_tab.py`) run today with no audio or ML
dependencies — they exercise the deterministic DP stage directly.
