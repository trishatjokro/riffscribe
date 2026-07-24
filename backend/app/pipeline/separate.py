"""Stage 2 (optional): isolate the guitar from a full-band mix.

Uses Demucs `htdemucs_6s`, the only mainstream open model with a dedicated
guitar stem. This is a P2 feature — v1 assumes the input is already a mostly
isolated guitar track and skips this stage.

NOTE: the 6-stem guitar output is noticeably weaker than Demucs' vocals/drums
stems; expect bleed that degrades downstream transcription.
"""

from __future__ import annotations

from pathlib import Path


def separate_guitar(audio_path: Path, out_dir: Path, model: str = "htdemucs_6s") -> Path:
    """Run source separation and return the path to the isolated guitar stem.

    Args:
        audio_path: input mix (wav/mp3).
        out_dir: where stems are written.
        model: Demucs model name; ``htdemucs_6s`` exposes a guitar stem.

    Returns:
        Path to the guitar stem wav.

    TODO(P2): shell out to / import demucs, select the `guitar` stem, handle the
    case where no guitar is detected.
    """
    raise NotImplementedError("Source separation is a P2 feature (see docs/architecture.md).")
