"""Slow original drones for Cosmic Drones.

Lengths, tempos, and collections are fixed before the notes. Seeds name studies.
Offsets are 0. Stasis and silence are intentional. Spectral change is not encoded.
"""

from __future__ import annotations

from tools.midi_io import BAR_TICKS_4_4, PPQ, bpm_to_us, effective_bpm

GENERATOR_VERSION = "1.0.0"
PACK_ID = "cosmic-drones"
PACK_NAME = "Cosmic Drones"
BAR = BAR_TICKS_4_4


class Part:
    def __init__(self, study, part_id, role, variation, channel, file_slug, max_poly, lo, hi):
        self.study = study
        self.part_id = part_id
        self.role = role
        self.variation = variation
        self.core = True
        self.channel = channel
        self.file_slug = file_slug
        self.monophonic = False
        self.max_poly = max_poly
        self.lo = lo
        self.hi = hi
        self.container_ticks = study["bars"] * BAR
        self.notes = []

    def add(self, start, duration, pitch, velocity, departure=False):
        end = start + duration
        if start < 0 or duration <= 0 or end > self.container_ticks:
            raise ValueError(f"{self.part_id} boundary {start}+{duration} of {self.container_ticks}")
        if not self.lo <= pitch <= self.hi:
            raise ValueError(f"{self.part_id} pitch {pitch} outside {self.lo}-{self.hi}")
        for other in self.notes:
            o0 = other["performed_start"]
            o1 = o0 + other["duration"]
            if start < o1 and o0 < end and other["pitch"] == pitch:
                raise ValueError(f"{self.part_id} same-pitch overlap {pitch}@{start}")
        active = 1
        for other in self.notes:
            o0 = other["performed_start"]
            o1 = o0 + other["duration"]
            if start < o1 and o0 < end:
                active += 1
        if active > self.max_poly:
            raise ValueError(f"{self.part_id} polyphony {active}")
        self.notes.append({
            "nominal_start": start,
            "offset": 0,
            "performed_start": start,
            "duration": duration,
            "pitch": pitch,
            "velocity": velocity,
            "channel": self.channel,
            "departure": departure,
        })

    def finish(self):
        ordered = sorted(self.notes, key=lambda note: (note["performed_start"], note["pitch"]))
        if len(ordered) < 1:
            raise ValueError(f"{self.part_id} empty")
        for index, note in enumerate(ordered, start=1):
            note["id"] = f"{self.part_id}.n{index:04d}"
        return {
            "id": self.part_id,
            "study_id": self.study["id"],
            "slug": self.study["slug"],
            "role": self.role,
            "variation": self.variation,
            "core": True,
            "channel": self.channel,
            "file_slug": self.file_slug,
            "path": f"midi/{self.study['slug']}/{self.file_slug}.mid",
            "monophonic": False,
            "max_poly": self.max_poly,
            "container_ticks": self.container_ticks,
            "container_bars": self.study["bars"],
            "bpm": self.study["bpm"],
            "tempo_us": self.study["tempo_us"],
            "notes": ordered,
        }


def foundation(study, variation):
    return Part(study, f"{study['id']}.foundation.{variation}", "foundation", variation, 0, f"foundation-{variation}", 2, 28, 60)


def field(study, variation):
    return Part(study, f"{study['id']}.field.{variation}", "harmonic-field", variation, 1, f"harmonic-field-{variation}", 8, 36, 84)


def signal(study, variation):
    return Part(study, f"{study['id']}.signal.{variation}", "distant-signal", variation, 2, f"distant-signal-{variation}", 3, 60, 96)


def at(bar, beats=0):
    return bar * BAR + beats * PPQ


def studies():
    rows = [
        {"id": "s01", "slug": "s01-common-tone", "title": "Common Tone", "bpm": 64, "bars": 8,
         "tonic": "D", "tonal_reference": "D", "collection_name": "D Dorian",
         "pitch_classes": [2, 4, 5, 7, 9, 11, 0], "departures": [], "seed": 6401,
         "identity": "A low D is joined by A, then both give way to F. The field enters one tone at a time. Signals are two distant calls with a long gap.",
         "limitations": "Variation B answers with the fifth first and leaves the middle two bars empty in the foundation. Do not stack A and B."},
        {"id": "s02", "slug": "s02-wide-fifth", "title": "Wide Fifth", "bpm": 50, "bars": 16,
         "tonic": "G", "tonal_reference": "G", "collection_name": "G Mixolydian",
         "pitch_classes": [7, 9, 11, 0, 2, 4, 5], "departures": [], "seed": 5002,
         "identity": "The foundation is only a fifth, held in two long plates. The field stays on three tones for eight bars, then shifts. Signals wait until the second half.",
         "limitations": "Sixteen bars at 50 BPM is longer than the preview. The preview is study 01 only."},
        {"id": "s03", "slug": "s03-rising-field", "title": "Rising Field", "bpm": 72, "bars": 16,
         "tonic": "E", "tonal_reference": "E", "collection_name": "E Phrygian",
         "pitch_classes": [4, 5, 7, 9, 11, 0, 2], "departures": [], "seed": 7203,
         "identity": "The foundation drops out for four bars. The field grows from one note to six. Variation B starts full and thins.",
         "limitations": "Six notes is under the field cap of eight. The file does not encode a filter opening."},
        {"id": "s04", "slug": "s04-night-register", "title": "Night Register", "bpm": 55, "bars": 32,
         "tonic": None, "tonal_reference": "no fixed tonic", "collection_name": "pitch-class set {0, 1, 5, 7, 10}",
         "pitch_classes": [0, 1, 5, 7, 10], "departures": ["Variation A signal at bar 24 uses D5 (74), outside the set."],
         "seed": 5504,
         "identity": "A 32-bar pedal swaps once, at the halfway bar. Variation B swaps earlier and adds a second foundation tone only in the last eight bars.",
         "limitations": "This study is too long for the 40-second preview. Silence in the signal lane is part of the piece."},
        {"id": "s05", "slug": "s05-signal-rain", "title": "Signal Rain", "bpm": 70, "bars": 8,
         "tonic": "C", "tonal_reference": "C", "collection_name": "C major",
         "pitch_classes": [0, 2, 4, 5, 7, 9, 11], "departures": [], "seed": 7005,
         "identity": "The foundation is one held C. The signals are the foreground: five separate calls. Variation B overlaps two signals and removes two others.",
         "limitations": "Signals stay within three notes at once. They are not percussion."},
        {"id": "s06", "slug": "s06-pedal-shift", "title": "Pedal Shift", "bpm": 60, "bars": 16,
         "tonic": "F", "tonal_reference": "F", "collection_name": "F Dorian",
         "pitch_classes": [5, 7, 8, 10, 0, 1, 3], "departures": [], "seed": 6006,
         "identity": "Variation A moves the foundation every four bars while the field holds still. Variation B holds the foundation and moves the field.",
         "limitations": "The still field is the point of variation A. It is not an unfinished sketch."},
        {"id": "s07", "slug": "s07-octave-drift", "title": "Octave Drift", "bpm": 75, "bars": 16,
         "tonic": "Bb", "tonal_reference": "Bb", "collection_name": "Bb natural minor",
         "pitch_classes": [10, 0, 1, 3, 5, 6, 8], "departures": [], "seed": 7507,
         "identity": "The same pitch classes sit in two octaves. Variation B delays the upper octave and shortens the lower one.",
         "limitations": "Octave choice is written as pitch. It is not a synth control."},
        {"id": "s08", "slug": "s08-open-fifth", "title": "Open Fifth", "bpm": 52, "bars": 8,
         "tonic": "A", "tonal_reference": "A", "collection_name": "A and E only",
         "pitch_classes": [9, 4], "departures": [], "seed": 5208,
         "identity": "Only a fifth, and a lot of silence. Variation B removes the second foundation entrance and adds one signal.",
         "limitations": "There is no third. Do not read the missing third as a later chord change."},
    ]
    for row in rows:
        if not 50 <= row["bpm"] <= 75:
            raise ValueError(row["bpm"])
        if row["bars"] not in (8, 16, 32):
            raise ValueError(row["bars"])
        row["tempo_us"] = bpm_to_us(row["bpm"])
        row["effective_bpm"] = effective_bpm(row["tempo_us"])
        row["meter"] = "4/4"
        row["bar_ticks"] = BAR
        row["ppq"] = PPQ
        row["stochastic_draws"] = 0
    return rows


def _s01(study):
    fa, fb = foundation(study, "a"), foundation(study, "b")
    fa.add(at(0), 5 * BAR, 38, 72)  # D2
    fa.add(at(3), 5 * BAR, 45, 64)  # A2 overlaps
    fb.add(at(0), 3 * BAR, 45, 70)
    fb.add(at(5), 3 * BAR, 38, 66)
    ha, hb = field(study, "a"), field(study, "b")
    for index, (bar, pitch) in enumerate([(0, 53), (2, 57), (4, 60), (6, 64)]):
        ha.add(at(bar), 3 * BAR if bar < 6 else 2 * BAR, pitch, 58 - index * 4)
    hb.add(at(1), 2 * BAR, 65, 60)
    hb.add(at(1), 2 * BAR, 69, 48)
    hb.add(at(4), 3 * BAR, 62, 54)
    sa, sb = signal(study, "a"), signal(study, "b")
    sa.add(at(1), BAR, 81, 70)
    sa.add(at(6), PPQ * 2, 86, 64)
    sb.add(at(2), BAR, 76, 68)
    sb.add(at(2, 2), PPQ * 2, 88, 60)
    return [fa, fb, ha, hb, sa, sb]


def _s02(study):
    fa, fb = foundation(study, "a"), foundation(study, "b")
    fa.add(at(0), 8 * BAR, 31, 68)  # G1
    fa.add(at(0), 8 * BAR, 38, 54)  # D2
    fa.add(at(8), 8 * BAR, 31, 64)
    fb.add(at(4), 8 * BAR, 38, 70)
    fb.add(at(4), 8 * BAR, 43, 50)  # G2
    ha, hb = field(study, "a"), field(study, "b")
    for pitch, vel in ((55, 50), (59, 46), (62, 42)):
        ha.add(at(2), 6 * BAR, pitch, vel)
    ha.add(at(10), 4 * BAR, 67, 48)
    hb.add(at(0), 4 * BAR, 55, 52)
    hb.add(at(8), 6 * BAR, 64, 46)
    hb.add(at(8), 6 * BAR, 71, 40)
    sa, sb = signal(study, "a"), signal(study, "b")
    sa.add(at(9), 2 * BAR, 79, 62)
    sa.add(at(14), BAR, 86, 58)
    sb.add(at(1), BAR, 91, 66)
    sb.add(at(12), 2 * BAR, 74, 54)
    return [fa, fb, ha, hb, sa, sb]


def _s03(study):
    fa, fb = foundation(study, "a"), foundation(study, "b")
    fa.add(at(0), 4 * BAR, 28, 66)  # E1
    fa.add(at(8), 8 * BAR, 40, 70)  # E2
    fb.add(at(0), 16 * BAR, 40, 60)
    fb.add(at(12), 4 * BAR, 35, 54)  # B1
    ha, hb = field(study, "a"), field(study, "b")
    pitches = [52, 53, 56, 59, 64, 68]
    for index, pitch in enumerate(pitches):
        ha.add(at(index * 2), (16 - index * 2) * BAR // 2 if False else max(BAR, (8 - index) * BAR // 2), pitch, 56 - index * 2)
    # fix durations to stay inside and keep poly reasonable
    ha.notes.clear()
    spans = [(0, 10, 52), (2, 8, 53), (4, 8, 55), (6, 6, 59), (8, 6, 64), (10, 4, 67)]
    for bar, bars, pitch in spans:
        ha.add(at(bar), bars * BAR, pitch, 50)
    hb.notes.clear()
    for bar, bars, pitch in [(0, 6, 67), (0, 6, 64), (0, 4, 59), (8, 6, 55), (10, 4, 53), (12, 4, 52)]:
        hb.add(at(bar), bars * BAR, pitch, 48)
    sa, sb = signal(study, "a"), signal(study, "b")
    sa.add(at(7), BAR, 88, 72)
    sa.add(at(15), PPQ, 76, 60)
    sb.add(at(3), 2 * BAR, 83, 64)
    return [fa, fb, ha, hb, sa, sb]


def _s04(study):
    fa, fb = foundation(study, "a"), foundation(study, "b")
    fa.add(at(0), 16 * BAR, 36, 64)  # C2
    fa.add(at(16), 16 * BAR, 43, 60)  # G2
    fb.add(at(0), 8 * BAR, 43, 66)
    fb.add(at(8), 16 * BAR, 36, 58)
    fb.add(at(24), 8 * BAR, 48, 54)  # C3 with C2
    ha, hb = field(study, "a"), field(study, "b")
    ha.add(at(4), 20 * BAR, 60, 46)
    ha.add(at(4), 20 * BAR, 67, 40)
    ha.add(at(18), 8 * BAR, 70, 42)
    hb.add(at(0), 12 * BAR, 55, 48)
    hb.add(at(12), 12 * BAR, 65, 44)
    hb.add(at(20), 8 * BAR, 58, 40)
    sa, sb = signal(study, "a"), signal(study, "b")
    sa.add(at(24), 2 * BAR, 74, 70, departure=True)  # D5, pc 2, outside {0,1,5,7,10}
    sb.add(at(2), BAR, 77, 62)
    sb.add(at(28), BAR, 82, 58)
    return [fa, fb, ha, hb, sa, sb]


def _s05(study):
    fa, fb = foundation(study, "a"), foundation(study, "b")
    fa.add(at(0), 8 * BAR, 36, 62)
    fb.add(at(2), 4 * BAR, 48, 68)
    ha, hb = field(study, "a"), field(study, "b")
    ha.add(at(0), 8 * BAR, 60, 44)
    ha.add(at(0), 8 * BAR, 64, 40)
    hb.add(at(3), 3 * BAR, 67, 50)
    hb.add(at(3), 3 * BAR, 72, 42)
    sa, sb = signal(study, "a"), signal(study, "b")
    for bar, pitch in ((0, 84), (2, 88), (3, 79), (5, 91), (7, 86)):
        sa.add(at(bar), PPQ, pitch, 74)
    sb.add(at(1), 2 * BAR, 84, 70)
    sb.add(at(1, 2), BAR, 91, 62)
    sb.add(at(6), PPQ * 2, 76, 66)
    return [fa, fb, ha, hb, sa, sb]


def _s06(study):
    fa, fb = foundation(study, "a"), foundation(study, "b")
    for index, pitch in enumerate((41, 46, 48, 53)):  # F2, Bb2, C3, F3
        fa.add(at(index * 4), 4 * BAR, pitch, 70 - index * 4)
    fb.add(at(0), 16 * BAR, 41, 66)
    ha, hb = field(study, "a"), field(study, "b")
    ha.add(at(0), 16 * BAR, 60, 48)
    ha.add(at(2), 14 * BAR, 65, 42)
    for index, pitch in enumerate((58, 63, 68, 70)):
        hb.add(at(index * 4), 4 * BAR, pitch, 52)
    sa, sb = signal(study, "a"), signal(study, "b")
    sa.add(at(7), 2 * BAR, 89, 64)
    sb.add(at(2), BAR, 82, 60)
    sb.add(at(11), BAR, 94, 58)
    return [fa, fb, ha, hb, sa, sb]


def _s07(study):
    fa, fb = foundation(study, "a"), foundation(study, "b")
    fa.add(at(0), 16 * BAR, 34, 68)  # Bb1
    fa.add(at(4), 8 * BAR, 41, 56)  # F2
    fb.add(at(0), 10 * BAR, 34, 64)
    fb.add(at(8), 8 * BAR, 46, 58)  # Bb2
    ha, hb = field(study, "a"), field(study, "b")
    ha.add(at(0), 12 * BAR, 58, 50)  # Bb3
    ha.add(at(2), 10 * BAR, 70, 44)  # Bb4
    ha.add(at(6), 6 * BAR, 63, 42)  # D#4 / Eb
    hb.add(at(4), 8 * BAR, 70, 52)
    hb.add(at(4), 8 * BAR, 65, 46)
    hb.add(at(10), 4 * BAR, 58, 40)
    sa, sb = signal(study, "a"), signal(study, "b")
    sa.add(at(9), BAR, 82, 66)
    sb.add(at(1), 2 * BAR, 87, 62)
    sb.add(at(14), PPQ, 75, 58)
    return [fa, fb, ha, hb, sa, sb]


def _s08(study):
    fa, fb = foundation(study, "a"), foundation(study, "b")
    fa.add(at(0), 3 * BAR, 33, 70)  # A1
    fa.add(at(0), 3 * BAR, 40, 54)  # E2
    fa.add(at(5), 3 * BAR, 45, 66)  # A2
    fb.add(at(0), 8 * BAR, 33, 64)
    fb.add(at(2), 4 * BAR, 40, 50)
    ha, hb = field(study, "a"), field(study, "b")
    ha.add(at(1), 4 * BAR, 57, 48)  # A3
    ha.add(at(1), 4 * BAR, 64, 40)  # E4
    hb.add(at(0), 2 * BAR, 69, 52)  # A4
    hb.add(at(4), 3 * BAR, 52, 46)  # E3
    sa, sb = signal(study, "a"), signal(study, "b")
    sa.add(at(6), PPQ * 3, 81, 68)  # A5
    sb.add(at(3), BAR, 88, 64)  # E6
    sb.add(at(3), BAR, 93, 50)  # A6
    return [fa, fb, ha, hb, sa, sb]


BUILDERS = {
    "s01": _s01, "s02": _s02, "s03": _s03, "s04": _s04,
    "s05": _s05, "s06": _s06, "s07": _s07, "s08": _s08,
}


def _sig(notes):
    return tuple((n["performed_start"], n["pitch"], n["duration"], n["velocity"]) for n in notes)


def assert_identities(parts):
    by_role = {}
    for part in parts:
        by_role.setdefault(part["role"], {}).setdefault(part["study_id"], {})[part["variation"]] = part
    report = []
    for role, studies_map in by_role.items():
        rhythms = {}
        for study_id, variations in studies_map.items():
            if _sig(variations["a"]["notes"]) == _sig(variations["b"]["notes"]):
                raise ValueError(f"{study_id} {role} variations match")
            rhythm = tuple(n["performed_start"] for n in variations["a"]["notes"])
            if rhythm in rhythms:
                raise ValueError(f"{study_id} {role} repeats {rhythms[rhythm]}")
            rhythms[rhythm] = study_id
            report.append({"study_id": study_id, "role": role, "a": len(variations["a"]["notes"]), "b": len(variations["b"]["notes"])})
    return {"pairs": report, "method": "each role's variations differ, and variation A entry times are not shared across studies"}


def compose():
    catalog_studies = studies()
    parts = []
    for study in catalog_studies:
        for part in BUILDERS[study["id"]](study):
            parts.append(part.finish())
    identity = assert_identities(parts)
    if len(parts) != 48:
        raise ValueError(len(parts))
    arrangement = {
        "id": "arrangement-preview-s01a",
        "path": "midi/arrangement.mid",
        "format": 1,
        "container_ticks": 8 * BAR,
        "bpm": 64,
        "tempo_us": bpm_to_us(64),
        "meter": "4/4",
        "description": "Study 01 variation A foundation, harmonic field, and distant signal. Full 8-bar container.",
        "tracks": [
            {"name": "Conductor", "source_part": None, "channel": None},
            {"name": "Foundation", "source_part": "s01.foundation.a", "channel": 0},
            {"name": "Harmonic Field", "source_part": "s01.field.a", "channel": 1},
            {"name": "Distant Signal", "source_part": "s01.signal.a", "channel": 2},
        ],
    }
    catalog = {
        "pack_id": PACK_ID,
        "pack_name": PACK_NAME,
        "catalog_version": GENERATOR_VERSION,
        "generator_version": GENERATOR_VERSION,
        "ppq": PPQ,
        "meter": {"numerator": 4, "denominator": 4, "bar_ticks": BAR},
        "pitched_range": [28, 96],
        "c4": 60,
        "note_policy": "note-only MIDI. Spectral change, filters, and spatial motion are not encoded.",
        "microtiming": "offset is 0 for every note; performed_start = nominal_start + offset",
        "stochastic_draws": 0,
        "seed_meaning": "Seeds identify studies. Nothing is drawn at random.",
        "core_part_count": 48,
        "reference_part_count": 0,
        "role_limits": {
            "foundation": "MIDI 28-60, at most 2 notes at once",
            "harmonic-field": "MIDI 36-84, at most 8 notes at once",
            "distant-signal": "MIDI 60-96, at most 3 notes at once",
        },
        "studies": [
            {key: study[key] for key in (
                "id", "slug", "title", "bpm", "tempo_us", "effective_bpm", "bars", "meter",
                "bar_ticks", "tonic", "tonal_reference", "collection_name", "pitch_classes",
                "departures", "seed", "identity", "limitations", "stochastic_draws",
            )}
            for study in catalog_studies
        ],
        "parts": [
            {
                "id": part["id"], "study_id": part["study_id"], "role": part["role"],
                "variation": part["variation"], "core": True, "channel": part["channel"],
                "path": part["path"], "notes": len(part["notes"]),
                "container_bars": part["container_bars"], "bpm": part["bpm"],
                "monophonic": False,
            }
            for part in parts
        ],
        "arrangement": arrangement,
        "preview_part_ids": ["s01.foundation.a", "s01.field.a", "s01.signal.a"],
        "stack_warning": "Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.",
    }
    score = {
        "pack_id": PACK_ID,
        "generator_version": GENERATOR_VERSION,
        "ppq": PPQ,
        "parts": parts,
        "arrangement": arrangement,
        "identity_check": identity,
    }
    return {"catalog": catalog, "score": score}
