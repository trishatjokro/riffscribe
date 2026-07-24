"""Stage 7 (export): tablature -> file formats the UI and users consume.

- ASCII tab: implemented here (no deps) for quick previews and tests.
- Guitar Pro `.gp5` / MusicXML: via PyGuitarPro / music21 (TODO), which alphaTab
  loads directly in the browser.
"""

from __future__ import annotations

from .types import Tablature


def to_ascii(tab: Tablature, cell_width: int = 4) -> str:
    """Render tablature as classic 6-line ASCII tab.

    Notes are laid out in time order across columns. This is a readable preview,
    not a rhythm-accurate score (that's what the .gp5/MusicXML exports are for).
    """
    n_strings = tab.tuning.num_strings
    # String labels, high string on the top line (reverse of internal low-first order).
    labels = ["e", "B", "G", "D", "A", "E"][:n_strings]

    ordered = sorted(tab.notes, key=lambda t: t.start)
    lines = [[] for _ in range(n_strings)]
    for tn in ordered:
        # Internal string 0 = low E -> render on the bottom line.
        row_from_top = (n_strings - 1) - tn.string
        cell = str(tn.fret)
        for r in range(n_strings):
            token = cell if r == row_from_top else "-" * len(cell)
            lines[r].append(token.ljust(cell_width, "-"))

    out = []
    for r in range(n_strings):
        out.append(f"{labels[r]}|" + "".join(lines[r]) + "|")
    return "\n".join(out)


def to_gp5(tab: Tablature, path) -> None:
    """Write a Guitar Pro 5 file (loadable by alphaTab).

    TODO(P0): build a guitarpro.Song via PyGuitarPro from `tab.notes`, mapping
    string/fret/timing and `tab.tuning`, then guitarpro.write(song, path).
    """
    raise NotImplementedError("GP5 export not yet implemented (P0).")


def to_musicxml(tab: Tablature, path) -> None:
    """Write MusicXML with a tab staff (loadable by alphaTab / music21).

    TODO(P0): construct a music21 Stream with TabStaff-style annotations.
    """
    raise NotImplementedError("MusicXML export not yet implemented (P0).")
