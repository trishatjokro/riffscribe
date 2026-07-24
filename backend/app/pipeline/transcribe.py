"""Stage 3–5: audio -> note events (pitch, onset, duration) + tempo.

v1 default backend is Spotify Basic Pitch (audio -> MIDI, Apache-2.0): fast to
stand up and emits note events directly. Because v1 targets a *monophonic*
line, a `crepe`/`librosa.pyin` backend produces cleaner single-note results and
is the intended swap once the pipeline is stable.
"""

from __future__ import annotations

from pathlib import Path

from .types import NoteEvents


def transcribe(audio_path: Path, backend: str = "basic_pitch") -> NoteEvents:
    """Transcribe an (ideally isolated, monophonic) guitar track to note events.

    Args:
        audio_path: guitar audio (wav/mp3).
        backend: ``"basic_pitch"`` (default) or ``"crepe"`` (mono-optimized).

    Returns:
        NoteEvents with an ordered list of notes and an estimated tempo.

    TODO(P0):
      * basic_pitch: call `basic_pitch.inference.predict`, map its note events
        to `Note`, then collapse to monophony (keep highest-confidence note in
        any overlap window).
      * crepe: f0 contour -> onset segmentation -> `Note`.
      * tempo: `librosa.beat.beat_track` for `NoteEvents.tempo_bpm`.
    """
    if backend not in {"basic_pitch", "crepe"}:
        raise ValueError(f"unknown transcription backend: {backend!r}")
    raise NotImplementedError("Transcription backend not yet implemented (P0).")
