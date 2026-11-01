"""Factual article draft. Not published."""

from __future__ import annotations

from tools.statements import AUDITION, ON_PICTURE, PREVIEW_LINE, PROGRAM, PUBLICATION, WARNING

TITLE = "Cosmic Drones is a note-only MIDI study pack"
SUBTITLE = "Eight slow studies, a matched byte check, and a simple-synth preview that is not a master"
TAGS = ["midi", "drone", "ambient", "music-production", "synthesis"]
TAG_LINE = "Tags: " + ", ".join(TAGS)

PARAGRAPHS = [
    "DRAFT. " + PUBLICATION,
    TAG_LINE,
    "The pack is eight studies of slow drones in 4/4. Tempos sit between 50 and 75 BPM. Lengths are 8, 16, or 32 bars, chosen before the notes. Each study has a foundation, a harmonic field, and distant signals. Each of those parts has two variations. All forty-eight files are core. Nothing in the pack is a hidden backing track.",
    "A variation has to change the phrase. Holding the same tones and only editing velocity does not count. Common Tone lets A enter under a held D. Wide Fifth is two long plates of a fifth. Rising Field grows from one tone to six, and variation B starts full and thins. Night Register is 32 bars and swaps its pedal once. Signal Rain keeps one foundation note and lets the signals speak. Pedal Shift moves either the foundation or the field, not both. Octave Drift stacks the same pitch classes in two octaves. Open Fifth uses only A and E.",
    "Foundation notes stay between MIDI 28 and 60, with at most two sounding. The field stays between 36 and 84, with at most eight. Signals stay between 60 and 96, with at most three. C4 is 60. The resolution is 960 ticks per quarter note. There is no microtiming offset. Spectral change is not in the file.",
    PROGRAM,
    "Filters, blooms, and spatial motion are not in the files. The preview synth uses a slow sine for the foundation, a triangle for the field, and a short high sine for the signals. That mapping is documented. It is not a program change.",
    "The primary preview is study 01, Common Tone, variation A, for all 8 bars: foundation, field, and signal together. The other studies are in the MIDI and are not in that audio file. "
    + PREVIEW_LINE
    + ". The film takes its audio from that preview file and shows the words "
    + ON_PICTURE
    + " on the picture and in the WebVTT captions.",
    AUDITION
    + " The validator reopened the MIDI bytes and compared them with the canonical score. That is a structural check. The sample peak written beside the preview is the peak of the integer mix. It is not LUFS and it is not a true-peak reading. Nothing in this build is claimed as a master.",
    "The stills are procedural illustrations of slow arcs and a pale dust field. They are not photographs of a session or of performers.",
    "When a public URL exists, use either the combined arrangement or the separate parts. " + WARNING,
    "Call to action: keep the pack local until the repository, branch, and deployment target are confirmed. Then publish the MIDI, the matched report, and the preview together. Do not publish this draft to Medium, Instagram, or X from the draft files alone.",
]


def markdown() -> str:
    body = "\n\n".join(PARAGRAPHS)
    return f"# {TITLE}\n\n{SUBTITLE}\n\n{body}\n"


def plain_text() -> str:
    lines = [TITLE, "", SUBTITLE, "", *PARAGRAPHS, ""]
    return "\n".join(lines) + "\n"
