"""Shared data types passed between pipeline stages.

Keeping these tiny and explicit means each stage (separate / transcribe / tab /
export) has a clear contract and can be unit-tested in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# Standard guitar tuning, low string (6th) to high string (1st), as MIDI note
# numbers: E2 A2 D3 G3 B3 E4. String index 0 == low E (6th string).
STANDARD_TUNING_MIDI = (40, 45, 50, 55, 59, 64)


@dataclass(frozen=True)
class Tuning:
    """A guitar tuning as open-string MIDI pitches, low string first."""

    open_strings: tuple[int, ...] = STANDARD_TUNING_MIDI
    name: str = "Standard (EADGBe)"

    @property
    def num_strings(self) -> int:
        return len(self.open_strings)


STANDARD_TUNING = Tuning()


@dataclass
class Note:
    """A single transcribed note event, before string/fret assignment."""

    pitch: int          # MIDI note number
    start: float        # seconds
    duration: float     # seconds
    confidence: float = 1.0   # 0..1, used to flag uncertain notes in the UI

    @property
    def end(self) -> float:
        return self.start + self.duration


@dataclass
class NoteEvents:
    """Output of the transcription stage: an ordered list of monophonic notes."""

    notes: list[Note] = field(default_factory=list)
    tempo_bpm: float | None = None
    sample_rate: int = 44100


@dataclass
class TabNote:
    """A note placed on the fretboard: which string, which fret, when."""

    string: int         # 0 == low E (6th string)
    fret: int           # 0 == open string
    start: float
    duration: float
    confidence: float = 1.0


@dataclass
class Tablature:
    """The final tab: fretted notes + the context needed to render/export it."""

    notes: list[TabNote] = field(default_factory=list)
    tuning: Tuning = STANDARD_TUNING
    tempo_bpm: float | None = None
    capo: int = 0
