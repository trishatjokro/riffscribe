"""Command-line entry point: `riffscribe path/to/audio.wav`.

Handy for testing the pipeline without the web stack.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe a guitar recording to tab.")
    parser.add_argument("audio", type=Path, help="input audio file (wav/mp3)")
    parser.add_argument("--backend", default="basic_pitch", choices=["basic_pitch", "crepe"])
    parser.add_argument("--capo", type=int, default=0)
    args = parser.parse_args()

    from .pipeline.transcribe import transcribe
    from .pipeline.tab import assign_tab
    from .pipeline.export import to_ascii

    events = transcribe(args.audio, backend=args.backend)
    tab = assign_tab(events, capo=args.capo)
    print(to_ascii(tab))


if __name__ == "__main__":
    main()
