# riffscribe — Architecture (v1)

The plan, version-controlled. This is the source of truth for *what* we're building
and *why*, grounded in a survey of prior art and open-source tooling (2026).

---

## 1. Framing & positioning

riffscribe is **not first** — Songsterr shipped an AI audio→tab feature in 2025, and
Klangio, Songscription, and audio2guitar are all racing in this space. That's
validation, not a blocker. Key findings from the prior-art survey:

- **Every automatic tool works on the same narrow case** we target: clean, isolated,
  mono/light-polyphonic guitar → *a draft that needs cleanup*. Our monophonic v1 aims
  exactly where the tech is real.
- **Everyone fails on "electric":** distortion, two guitars at once, palm mutes / bends /
  slides, dense mixes. That failure zone is the strategic opening *and* the thing to
  under-promise on.
- **The big catalogs (Songsterr core, Ultimate Guitar, Yousician) are human-made.** So
  "type a song name → tab" is a **licensing/catalog problem**, not an ML one. Upload-audio
  is the real product; song-name is a thin data/rights layer.
- **Winning UX everyone converges on:** *"AI draft + dead-easy manual correction."*

**Positioning statement:** *instant first-draft tab you fix in seconds — not perfect
transcription.*

## 2. Two input paths, one engine

```
      ┌─ Upload audio (mp3/wav) ─────────────┐
Input ┤                                      ├─▶ [ ENGINE ] ─▶ Interactive tab
      └─ Type song name ─▶ resolve to audio ─┘
```

- **Upload = the ML product** (v1 core). Fully original, no rights issues.
- **Song-name = thin lookup layer.** v1: the user still supplies/points to the audio; a
  true catalog is a P3 licensing decision, not code.

## 3. Transcription pipeline

```
audio
 └▶ 1. Preprocess      resample, mono, normalize                    [librosa]
 └▶ 2. (opt) Separate  pull guitar stem from a full mix             [Demucs htdemucs_6s · MIT]
 └▶ 3. Pitch + onsets  v1 mono: clean single-note tracking          [CREPE · MIT / librosa.pyin]
                       easy default: note events → MIDI             [Basic Pitch · Apache-2.0]
 └▶ 4. Note events     (pitch, onset, duration, confidence) → MIDI
 └▶ 5. Beat/tempo      barlines + rhythm quantization               [librosa]
 └▶ 6. Notes → TAB     DP shortest-path fret optimizer (Sayegh),    [music21 · BSD + PyGuitarPro · LGPL]
                       export .gp5 / MusicXML
 └▶ 7. Render + play   synchronized scrolling tab in the browser    [alphaTab · MPL-2.0]
```

**Stage 3 note:** because v1 is *monophonic*, a dedicated pitch tracker (CREPE / pyin)
gives cleaner single-note results than a polyphonic model — but **Basic Pitch** is the
fastest thing to stand up and emits MIDI directly. Plan: ship on Basic Pitch, keep CREPE
as the mono-optimized swap.

**Stage 6 ("which fret?")** is the reliable part: the same pitch maps to many string/fret
positions, solved as a shortest-path problem minimizing hand movement + fret span,
tuning-aware (EADGBe default, overridable). Rooted in Sayegh's Optimum Path Paradigm (1989).

## 4. UI/UX (built for people who can't read notation)

- **Upload/search → progress → scrolling tab that plays back in sync** (highlighted note,
  Songsterr-style — alphaTab renders *and* plays natively).
- Simple controls: **speed slider, loop-a-section, count-in, tuning/capo toggle.**
- **Confidence surfacing + one-click correction** — non-negotiable; the honest-UX pattern
  every credible tool lands on.
- **Export:** Guitar Pro `.gp5`, MusicXML, ASCII tab.

## 5. Recommended stack (ships-today path)

- **Frontend:** React + Vite + **alphaTab** (MPL-2.0) — loads `.gp5`/MusicXML, synced
  cursor playback.
- **Backend:** Python + **FastAPI**, async job queue (transcription = seconds–minutes),
  object storage for uploads.
- **Engine:** **Demucs → Basic Pitch → DP tab optimizer (music21 + PyGuitarPro) →
  alphaTab.** All permissively licensed, all runnable now.
- **R&D upgrade path (P3+):** swap stages 3–6 for a guitar-native model (**TabCNN /
  FretNet**, trained on **GuitarSet**) that predicts string+fret directly — higher ceiling,
  less mature, generalizes poorly to distorted mixes today.

## 6. Phased roadmap

| Phase | Goal |
|---|---|
| **P0 — Vertical slice** | Upload a clean solo-guitar clip → playable, exportable tab. Proves the whole chain end-to-end. |
| **P1 — Usability** | Synced playback, looping, manual correction, tuning options. |
| **P2 — Full-mix input** | Add Demucs separation (accept the accuracy hit). |
| **P3 — Reach** | Song-name catalog (licensing), polyphony/chords, technique detection (bends/slides) — the genuine frontier. |

## 7. Honest risk register

- **Transcription accuracy on real electric recordings** (distortion, effects) — top risk;
  degrades across *every* tool on the market.
- **Demucs 6-stem guitar output is weaker** than its vocals/drums stems → bleed cascades
  into transcription.
- **Technique (bends / slides / palm mutes) is essentially unsolved** in open tooling —
  expect to drop it in v1.
- **Song-name → audio = copyright/licensing**, not code.
- **"As good as Songsterr" is a moonshot** — their fidelity is *human*. Matching it
  automatically is the whole hard bet. Position as *first-draft*, not *perfect*.

## 8. Prior art & references

**Products:** Songsterr (human catalog + 2025 AI feature), Ultimate Guitar (human),
Chordify (auto chords only), Klangio/Guitar2Tabs (auto, guitar-specific), AnthemScore
(auto, general), Moises (chords + stems), Yousician (human), Soundslice (human aid).

**Models / tooling:** Basic Pitch (Apache-2.0), Demucs (MIT), CREPE (MIT), MT3 / YourMT3
(Apache-2.0), Omnizart (MIT), TabCNN & FretNet (research, GuitarSet), Fretting-Transformer
(2025 SOTA MIDI→tab, no code released), music21 (BSD), PyGuitarPro (LGPL), alphaTab (MPL-2.0).

**Datasets:** GuitarSet (MIT), DadaGP, IDMT-SMT-Guitar.
