"""Stage 6: note events -> tablature (string + fret assignment).

The "which fret?" problem: a given pitch is playable at several (string, fret)
positions. We pick the sequence of positions that is easiest to play, framed as
a shortest-path problem over candidate positions (Sayegh's Optimum Path
Paradigm, 1989) and solved with dynamic programming / Viterbi.

Unlike the ML stages, this is deterministic and reliable, so it's implemented
here rather than stubbed.
"""

from __future__ import annotations

from .types import Note, NoteEvents, Tablature, TabNote, Tuning, STANDARD_TUNING

# Cost weights — tunable. Higher = more strongly avoided.
_W_FRET_HEIGHT = 0.4    # prefer lower frets (open-position playing)
_W_HAND_MOVE = 1.0      # prefer staying near the previous fret (minimize shifts)
_W_OPEN_STRING_BONUS = 0.3   # slight preference for open strings

MAX_FRET = 24


def _candidates(pitch: int, tuning: Tuning, capo: int) -> list[tuple[int, int]]:
    """All playable (string, fret) positions for a pitch in this tuning."""
    positions: list[tuple[int, int]] = []
    for string_idx, open_pitch in enumerate(tuning.open_strings):
        fret = pitch - open_pitch - capo
        if 0 <= fret <= MAX_FRET:
            positions.append((string_idx, fret))
    return positions


def _position_cost(fret: int) -> float:
    """Static cost of a single position, independent of what came before."""
    cost = _W_FRET_HEIGHT * fret
    if fret == 0:
        cost -= _W_OPEN_STRING_BONUS
    return cost


def _transition_cost(prev: tuple[int, int], cur: tuple[int, int]) -> float:
    """Cost of moving the fretting hand from one position to the next.

    Dominated by how far the hand slides along the neck (fret distance).
    Open strings (fret 0) don't require the hand, so they don't anchor position.
    """
    prev_fret, cur_fret = prev[1], cur[1]
    if prev_fret == 0 or cur_fret == 0:
        return 0.0
    return _W_HAND_MOVE * abs(prev_fret - cur_fret)


def assign_tab(
    events: NoteEvents,
    tuning: Tuning = STANDARD_TUNING,
    capo: int = 0,
) -> Tablature:
    """Assign each note to a string/fret via DP, minimizing playing effort.

    Args:
        events: monophonic note events from the transcription stage.
        tuning: target tuning (open-string pitches). Defaults to standard.
        capo: capo fret (0 = none).

    Returns:
        A `Tablature` with one `TabNote` per input note. Notes with no playable
        position in this tuning are dropped (and should be surfaced upstream).
    """
    notes: list[Note] = events.notes
    if not notes:
        return Tablature(tuning=tuning, tempo_bpm=events.tempo_bpm, capo=capo)

    # Viterbi over candidate positions per note.
    # dp[i] maps each candidate position -> (min cumulative cost, back-pointer).
    per_note_candidates: list[list[tuple[int, int]]] = [
        _candidates(n.pitch, tuning, capo) for n in notes
    ]

    dp: list[dict[tuple[int, int], float]] = []
    back: list[dict[tuple[int, int], tuple[int, int] | None]] = []

    for i, cands in enumerate(per_note_candidates):
        dp_i: dict[tuple[int, int], float] = {}
        back_i: dict[tuple[int, int], tuple[int, int] | None] = {}
        for pos in cands:
            static = _position_cost(pos[1])
            if i == 0:
                dp_i[pos] = static
                back_i[pos] = None
            else:
                best_prev, best_cost = None, float("inf")
                for prev_pos, prev_cost in dp[i - 1].items():
                    c = prev_cost + _transition_cost(prev_pos, pos) + static
                    if c < best_cost:
                        best_cost, best_prev = c, prev_pos
                dp_i[pos] = best_cost
                back_i[pos] = best_prev
        dp.append(dp_i)
        back.append(back_i)

    # Backtrack from the cheapest final position.
    tab_notes: list[TabNote] = []
    # Find the last note index that actually had candidates.
    last = len(notes) - 1
    while last >= 0 and not dp[last]:
        last -= 1
    if last < 0:
        return Tablature(tuning=tuning, tempo_bpm=events.tempo_bpm, capo=capo)

    pos: tuple[int, int] | None = min(dp[last], key=dp[last].get)
    chosen: list[tuple[int, tuple[int, int]]] = []
    i = last
    while i >= 0 and pos is not None:
        if dp[i]:
            chosen.append((i, pos))
            pos = back[i][pos]
        i -= 1
    chosen.reverse()

    for note_idx, (string, fret) in chosen:
        n = notes[note_idx]
        tab_notes.append(
            TabNote(string=string, fret=fret, start=n.start,
                    duration=n.duration, confidence=n.confidence)
        )

    return Tablature(
        notes=tab_notes, tuning=tuning, tempo_bpm=events.tempo_bpm, capo=capo
    )
