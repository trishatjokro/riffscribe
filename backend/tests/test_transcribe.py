"""Tests for the monophonic reduction step.

The Basic Pitch call itself needs the ML runtime + audio, so it's exercised
manually / in integration. The `to_monophonic` collapse is pure logic and is
the part most likely to have edge-case bugs, so it's unit-tested here.
"""

from app.pipeline.transcribe import to_monophonic
from app.pipeline.types import Note


def _sorted(notes):
    return sorted(notes, key=lambda n: (n.start, -n.confidence))


def test_sequential_notes_all_kept():
    notes = [
        Note(pitch=40, start=0.0, duration=0.4, confidence=0.9),
        Note(pitch=45, start=0.5, duration=0.4, confidence=0.9),
        Note(pitch=50, start=1.0, duration=0.4, confidence=0.9),
    ]
    assert len(to_monophonic(_sorted(notes))) == 3


def test_overlap_keeps_higher_confidence():
    # Two notes sounding together -> keep the louder one.
    quiet = Note(pitch=40, start=0.0, duration=0.5, confidence=0.3)
    loud = Note(pitch=47, start=0.1, duration=0.5, confidence=0.8)
    mono = to_monophonic(_sorted([quiet, loud]))
    assert len(mono) == 1
    assert mono[0].pitch == 47


def test_chord_collapses_to_one_note():
    # A 3-note chord struck at once -> a single monophonic note (the loudest).
    chord = [
        Note(pitch=40, start=0.0, duration=0.6, confidence=0.4),
        Note(pitch=47, start=0.0, duration=0.6, confidence=0.9),
        Note(pitch=52, start=0.01, duration=0.6, confidence=0.6),
    ]
    mono = to_monophonic(_sorted(chord))
    assert len(mono) == 1
    assert mono[0].pitch == 47


def test_tiny_overlap_within_eps_is_tolerated():
    # A hair of overlap (< eps) from imperfect offsets shouldn't merge notes.
    a = Note(pitch=40, start=0.0, duration=0.50, confidence=0.9)
    b = Note(pitch=45, start=0.51, duration=0.40, confidence=0.9)  # ~0.01 gap after a.end-ish
    mono = to_monophonic(_sorted([a, b]))
    assert len(mono) == 2


def test_empty_is_safe():
    assert to_monophonic([]) == []
