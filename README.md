# 🎸 Riffscribe

**Turn any guitar recording into an editable, playable tab — an open-source, electric-first automated transcriber.**

Upload a riff (or point at a song), and riffscribe generates guitar tablature you can
play back in sync, slow down, loop, and fix in seconds. It's built for players who
learn by ear and can't read standard notation.

> **Honest framing:** riffscribe produces an *instant first draft*, not a perfect
> transcription. Automatic music transcription is genuinely hard — especially for
> distorted electric guitar in a full mix. The goal is to save you the tedious first
> pass, then make corrections trivial. See [`docs/architecture.md`](docs/architecture.md)
> for the honest risk register.

---

## Status

🚧 **Pre-alpha / scaffolding.** The plan is version-controlled first (see the
architecture doc); the P0 vertical slice is being built into this skeleton.

## How it works

```
audio ─▶ (opt) separate guitar stem ─▶ transcribe to notes ─▶ assign strings/frets ─▶ render playable tab
         Demucs                        Basic Pitch            DP fret-optimizer        alphaTab (browser)
```

The v1 target is a **single monophonic guitar line** (riffs / melodies / solos) —
that's where today's transcription tech is actually reliable. Chords, full-mix
separation, and technique detection (bends, slides) are on the roadmap, not in v1.

Full pipeline, model choices, and roadmap: **[`docs/architecture.md`](docs/architecture.md)**.

## Tech stack

| Layer | Choice | License |
|---|---|---|
| Source separation | [Demucs](https://github.com/facebookresearch/demucs) `htdemucs_6s` | MIT |
| Transcription (audio→MIDI) | [Spotify Basic Pitch](https://github.com/spotify/basic-pitch) | Apache-2.0 |
| Mono pitch (optional) | [CREPE](https://github.com/marl/crepe) / `librosa.pyin` | MIT |
| Notes → tab | DP fret-optimizer + [music21](https://github.com/cuthbertLab/music21) + [PyGuitarPro](https://github.com/Perlence/PyGuitarPro) | BSD / LGPL |
| Web rendering + playback | [alphaTab](https://github.com/coderline/alphaTab) | MPL-2.0 |
| Backend API | FastAPI | MIT |
| Frontend | React + Vite | MIT |

## Repo layout

```
riffscribe/
├── docs/architecture.md   # the plan: pipeline, model picks, risks, roadmap
├── backend/               # Python ML engine + FastAPI
│   └── app/pipeline/      # separate → transcribe → tab → export
├── frontend/              # React + alphaTab UI
└── samples/               # royalty-free test clips ONLY (no copyrighted songs)
```

## Development

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload

# frontend
cd frontend
npm install
npm run dev
```

## A note on copyright

riffscribe (the tool) is MIT-licensed and free to use. **Do not commit copyrighted
audio to this repo.** Test fixtures use royalty-free / Creative Commons clips or
[GuitarSet](https://zenodo.org/records/3371780) (MIT). Distributing tabs of
copyrighted songs is a separate legal question that never needs to touch this codebase.

## License

[MIT](LICENSE)
