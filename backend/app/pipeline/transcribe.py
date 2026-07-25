"""Stage 3-5: audio -> note events (pitch, onset, duration) + tempo.

v1 default backend is Spotify Basic Pitch (audio -> MIDI, Apache-2.0): fast to
stand up and emits note events directly. Basic Pitch is polyphonic, so for our
monophonic v1 target we collapse its output to a single line (highest-confidence
note wins in any overlap window). A `crepe`/`librosa.pyin` backend produces
cleaner single-note results and is the intended swap once the pipeline is stable.
"""

from __future__ import annotations

from pathlib import Path

from .types import Note, NoteEvents

# Restrict transcription to a guitar's range so Basic Pitch doesn't invent
# sub-bass or whistle-high artifacts. Low E is ~82 Hz; a 24th-fret high-E bend
# lands around ~1.3 kHz, so we pad the window slightly on both ends.
_GUITAR_MIN_HZ = 70.0
_GUITAR_MAX_HZ = 1400.0

# Two note events closer than this (seconds) at the same time are treated as
# simultaneous (a chord / model artifact) and reduced to one for the mono line.
_OVERLAP_EPS = 0.03


def transcribe(audio_path: Path | str, backend: str = "basic_pitch") -> NoteEvents:
    """Transcribe an (ideally isolated, monophonic) guitar track to note events.

    Args:
        audio_path: guitar audio (wav/mp3).
        backend: ``"basic_pitch"`` (default) or ``"crepe"`` (mono-optimized).

    Returns:
        NoteEvents with an ordered, monophonic list of notes and an estimated tempo.
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(audio_path)

    if backend == "basic_pitch":
        return _transcribe_basic_pitch(audio_path)
    if backend == "crepe":
        raise NotImplementedError("The crepe (mono) backend is not wired up yet.")
    raise ValueError(f"unknown transcription backend: {backend!r}")


def _transcribe_basic_pitch(audio_path: Path) -> NoteEvents:
    """Run Basic Pitch and reduce its polyphonic output to a monophonic line."""
    # Imported lazily: pulls in the (heavy) ML runtime only when actually used,
    # so the rest of the package stays importable without it (tests, tab stage).
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import predict

    _model_out, _midi, note_events = predict(
        str(audio_path),
        _model_path(ICASSP_2022_MODEL_PATH),
        onset_threshold=0.5,
        frame_threshold=0.3,
        minimum_note_length=70.0,          # ms — drop blips shorter than a fast note
        minimum_frequency=_GUITAR_MIN_HZ,
        maximum_frequency=_GUITAR_MAX_HZ,
        melodia_trick=True,
    )

    # note_events: list of (start_s, end_s, pitch_midi, amplitude, pitch_bends)
    notes = [
        Note(
            pitch=int(pitch),
            start=float(start),
            duration=max(float(end) - float(start), 1e-3),
            confidence=float(amplitude),
        )
        for (start, end, pitch, amplitude, *_bends) in note_events
    ]
    # Earliest first; on ties, most-confident first so it "wins" the window.
    notes.sort(key=lambda n: (n.start, -n.confidence))

    return NoteEvents(
        notes=to_monophonic(notes),
        tempo_bpm=_estimate_tempo(audio_path),
    )


def _model_path(default):
    """Prefer the ONNX serialization of the Basic Pitch model when present.

    The library's default points at a TensorFlow SavedModel, whose loader is
    heavy and flaky across platforms/Python versions. We install the ``[onnx]``
    runtime, so use the equivalent ``.onnx`` weights if they're on disk and fall
    back to the default otherwise.
    """
    from pathlib import Path

    base = Path(str(default))
    onnx = base.with_name(base.name + ".onnx")
    return str(onnx if onnx.exists() else base)


def to_monophonic(notes: list[Note], overlap_eps: float = _OVERLAP_EPS) -> list[Note]:
    """Reduce a (time-sorted) note list to a single non-overlapping line.

    When a note starts before the previously kept note has ended, the two are
    sounding together — a chord or a transcription artifact. For a monophonic
    tab we keep whichever is more confident and drop the other. This is a
    deterministic, dependency-free step, so it's unit-tested directly.
    """
    mono: list[Note] = []
    for n in notes:
        if mono and n.start < mono[-1].end - overlap_eps:
            if n.confidence > mono[-1].confidence:
                mono[-1] = n  # louder/clearer note wins this window
        else:
            mono.append(n)
    return mono


def _estimate_tempo(audio_path: Path) -> float | None:
    """Best-effort tempo estimate; returns None if it can't be determined."""
    try:
        import librosa

        y, sr = librosa.load(str(audio_path), mono=True)
        tempo, _beats = librosa.beat.beat_track(y=y, sr=sr)
        # librosa may return a 0-d/1-element array depending on version.
        import numpy as np

        return round(float(np.atleast_1d(tempo)[0]), 1)
    except Exception:
        return None
