"""Tests for the deterministic fret-assignment stage.

These don't need audio or ML models — they exercise the DP optimizer directly,
so they run in CI today (before the transcription stage is implemented).
"""

from app.pipeline.export import to_ascii
from app.pipeline.tab import assign_tab
from app.pipeline.types import STANDARD_TUNING, Note, NoteEvents


def _events(pitches: list[int]) -> NoteEvents:
    return NoteEvents(
        notes=[Note(pitch=p, start=float(i) * 0.5, duration=0.5) for i, p in enumerate(pitches)]
    )


def test_open_low_e_maps_to_string0_fret0():
    tab = assign_tab(_events([40]))  # E2 = open low E
    assert len(tab.notes) == 1
    assert (tab.notes[0].string, tab.notes[0].fret) == (0, 0)


def test_prefers_low_frets_for_a_single_note():
    # A2 (45) is open A string (string 1, fret 0) or fret 5 on low E.
    tab = assign_tab(_events([45]))
    assert (tab.notes[0].string, tab.notes[0].fret) == (1, 0)


def test_minimizes_hand_movement_across_a_run():
    # An ascending run should stay in a compact position rather than leaping
    # across the neck. We just assert the total fret span stays small.
    pitches = [40, 43, 45, 47, 50]  # E2 G2 A2 B2 D3
    tab = assign_tab(_events(pitches))
    fretted = [n.fret for n in tab.notes if n.fret > 0]
    if fretted:
        assert max(fretted) - min(fretted) <= 5


def test_unplayable_pitch_is_dropped():
    # Way below the lowest string -> no candidate positions.
    tab = assign_tab(_events([12]))  # C0
    assert tab.notes == []


def test_ascii_render_has_six_lines():
    tab = assign_tab(_events([40, 45, 50]))
    lines = to_ascii(tab).splitlines()
    assert len(lines) == STANDARD_TUNING.num_strings == 6


def test_empty_input_is_safe():
    tab = assign_tab(NoteEvents(notes=[]))
    assert tab.notes == []
