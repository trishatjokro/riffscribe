"""The transcription pipeline: audio -> (separate) -> transcribe -> tab -> export.

Data flows as small, explicit dataclasses (see `types.py`) so each stage is
independently testable and swappable. The v1 target is a single monophonic
guitar line; polyphony and technique detection are out of scope (see
docs/architecture.md).
"""

from .types import STANDARD_TUNING, Note, NoteEvents, Tablature, TabNote, Tuning

__all__ = [
    "Note",
    "NoteEvents",
    "TabNote",
    "Tablature",
    "Tuning",
    "STANDARD_TUNING",
]
