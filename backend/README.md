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
| Audio → notes | `transcribe.py` | stub (P0) — Basic Pitch / CREPE |
| Notes → string+fret | `tab.py` | **implemented** (DP fret optimizer) |
| Export (ASCII / .gp5 / MusicXML) | `export.py` | ASCII done; .gp5/MusicXML stub (P0) |

## Tests

```bash
pytest
```

The fret-optimizer tests (`tests/test_tab.py`) run today with no audio or ML
dependencies — they exercise the deterministic DP stage directly.
