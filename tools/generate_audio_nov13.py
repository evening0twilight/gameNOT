"""Original procedural score and Foley for 夜潮事务所 0.18. No external samples.

Render exact cyclic phrases by wrapping notes and delay tails into the loop.
Existing asset directories and historical receipts are untouched.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import struct
import wave
from array import array
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'game/assets/product018/audio/nov13'
RATE = 24000
TAU = math.tau
sin = math.sin
exp = math.exp

# Eight-bar original lead lines, sparse beds. Each tuple gives beat, MIDI note.
SCORES = {
    'daily': (78, 'felt', [
        (53, 60, 65, 69), (50, 57, 65, 69), (46, 58, 62, 65), (48, 55, 62, 67),
        (53, 60, 65, 69), (52, 59, 62, 67), (50, 57, 62, 65), (48, 55, 62, 70),
    ], [(0, 69), (1.5, 72), (3, 74), (5, 69), (7, 65), (9, 65), (10.5, 67),
        (13, 67), (15, 74), (16, 72), (17.5, 69), (19, 67), (22, 71),
        (24, 69), (26, 65), (28.5, 62), (30, 67)]),
    'grave': (58, 'bow', [
        (45, 57, 60, 64), (45, 55, 59, 64), (41, 53, 57, 60), (40, 52, 55, 62),
        (38, 50, 53, 60), (41, 53, 57, 64), (45, 52, 59, 60), (40, 52, 57, 62),
    ], [(1, 64), (6, 60), (9, 57), (14, 59), (17, 57), (22, 60), (25, 59), (29, 55)]),
    'battle': (82, 'metal', [
        (45, 57, 60, 64), (45, 57, 62, 64), (43, 55, 60, 62), (40, 52, 55, 59),
        (45, 57, 60, 64), (46, 58, 62, 65), (43, 55, 60, 62), (40, 52, 57, 59),
    ], [(2.5, 64), (6, 62), (7.5, 60), (10, 62), (13.5, 59), (15, 64),
        (18.5, 64), (22, 65), (23.5, 62), (26, 62), (29.5, 59), (31, 55)]),
    'battle_high': (106, 'metal', [
        (45, 57, 60, 64), (45, 58, 62, 64), (41, 53, 57, 60), (40, 52, 55, 59),
        (45, 57, 60, 64), (43, 55, 58, 62), (41, 53, 57, 60), (40, 52, 56, 62),
    ], [(1.5, 69), (2, 64), (3.5, 67), (5.5, 70), (7, 64), (8.5, 65), (10, 60),
        (11.5, 64), (13, 59), (15, 64), (16.5, 69), (18, 64), (19.5, 67), (21, 70),
        (23, 62), (24.5, 65), (26, 60), (27.5, 65), (29, 68), (31, 62)]),
}


def hz(note):
    return 440 * 2 ** ((note - 69) / 12)


def envelope(t, duration, attack=.004, release=.035):
    return min(1.0, t / attack, max(0.0, (duration - t) / release))


def write(name, channels, rms_target, max_peak, design, kind):
    mixed = [x for channel in channels for x in channel]
    peak = max(map(abs, mixed))
    rms = math.sqrt(sum(x * x for x in mixed) / len(mixed))
    gain = min(rms_target / rms, max_peak / peak)
    interleaved = array('h', (round(v * gain * 32767) for frame in zip(*channels) for v in frame))
    if struct.pack('=h', 1) != struct.pack('<h', 1):
        interleaved.byteswap()
    path = OUT / (name + '.wav')
    with wave.open(str(path), 'wb') as file:
        file.setparams((len(channels), 2, RATE, 0, 'NONE', 'not compressed'))
        file.writeframes(interleaved.tobytes())
    return {
        'id': name, 'kind': kind, 'path': str(path.relative_to(ROOT)), 'design': design,
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'seconds': len(channels[0]) / RATE,
        'channels': len(channels), 'sample_rate': RATE, 'rms': round(rms * gain, 7),
        'peak': round(peak * gain, 7),
    }


def score(name, bpm, instrument, chords, melody):
    beat = 60 / bpm
    frames = round(RATE * 32 * beat)
    left = array('f', [0]) * frames
    right = array('f', [0]) * frames

    def note(at, midi, length, amp, voice, pan=0.0):
        origin = round(at * beat * RATE)
        duration = length * beat
        freq = hz(midi)
        direct_l = amp * math.sqrt((1 - pan) / 2)
        direct_r = amp * math.sqrt((1 + pan) / 2)
        delay = round((.18 + .09 * (pan + 1)) * RATE)
        for i in range(round(duration * RATE)):
            t = i / RATE
            phase = TAU * freq * t
            if voice == 'bed':
                sample = (sin(phase + .045 * sin(t * 2)) + .16 * sin(phase * 2 + .6)
                          + .16 * sin(phase * .998))
                sample *= envelope(t, duration, beat * .75, beat * 1.4)
            elif voice == 'bow':
                sample = (sin(phase + .14 * sin(28 * t)) + .28 * sin(2 * phase)
                          + .1 * sin(3 * phase + .3))
                sample *= envelope(t, duration, .27, .35) * (.75 + .25 * sin(4 * t))
            elif voice == 'kick':
                sample = sin(TAU * (freq * t + 38 * (1 - exp(-t * 20)) / 20))
                sample *= envelope(t, duration) * exp(-t * 17)
            else:
                felt = voice == 'felt'
                sample = sin(phase + (.3 if felt else .67) * exp(-t * 6) * sin(phase * 2))
                sample += .20 * sin(phase * (2.003 if felt else 2.15)) * exp(-t * 5)
                sample += .10 * sin(phase * (3.002 if felt else 3.74)) * exp(-t * 14)
                sample *= envelope(t, duration, .008, .17) * exp(-t * (2.2 if felt else 4.6))
            j = (origin + i) % frames
            k = (j + delay) % frames
            left[j] += sample * direct_l
            right[j] += sample * direct_r
            left[k] += sample * direct_r * .13
            right[k] += sample * direct_l * .13

    for bar, chord in enumerate(chords):
        for idx, pitch in enumerate(chord):
            note(bar * 4 - .30 + .11 * idx, pitch, 4.9, .014 if idx else .029,
                 'bed', [-.10, -.36, .41, .19][idx])
        if name == 'daily':
            note(bar * 4 + 2.5, chord[1], 1.6, .022, 'felt', -.45)
        elif name.startswith('battle'):
            urgent = name == 'battle_high'
            for offset in ((0, .75, 1.5, 2, 2.75, 3.5) if urgent else (0, 1.5, 2.5)):
                note(bar * 4 + offset, chord[0] - 9, .55, .055 if urgent else .038, 'kick')
            if urgent:
                for offset in (.5, 1.25, 2.25, 3.25):
                    note(bar * 4 + offset, chord[1], .44, .023, 'metal', -.38 if offset < 2 else .43)

    for index, (at, pitch) in enumerate(melody):
        length = 3.2 if instrument == 'bow' else (1.9 if instrument == 'felt' else .85)
        note(at, pitch, length, .07 if instrument != 'bow' else .043, instrument,
             .20 if index % 2 == 0 else -.13)

    return write(name, (left, right), .041 if name == 'battle_high' else .034, .20,
                 f'{bpm} BPM; 8 bars; {instrument} lead, rotating harmony, wrapped tails', 'music')


# Single purpose per cue. Frequencies below are synthesized body resonances, not samples.
FOLEY = {
    'attack': (.24, 'Hard hit: fast crack, body impact, two short metal modes.'),
    'push': (.27, 'Shove: rough cloth drag against the ground, ending in a dull stop.'),
    'pickup': (.23, 'Lift: fabric movement and two rising strap clicks.'),
    'drop': (.21, 'Set down: double low contact, fabric settles.'),
    'injury': (.31, 'Warning: muted impact, two descending dissonant accents; no voice.'),
    'objective': (.55, 'Completion: warm three-note upward cadence with soft decay.'),
    'machine_scout': (.31, 'Mobile scout: accelerating servo and quick rattling drive.'),
    'machine_welder': (.33, 'Welder: two gritty arcs with short electrical fizz.'),
    'machine_hauler': (.42, 'Rail hauler: heavy low motor and three rail joints.'),
    'machine_skimmer': (.34, 'Water skimmer: watery rising flick and fading electric sizzle.'),
    'machine_relay': (.31, 'Relay: relay contact, second thin click, short mains hum.'),
    'machine_sentinel': (.40, 'Sentinel: charged low sweep then clean beam onset.'),
}


def foley(name, duration, seed, design):
    randomizer = random.Random(seed)
    mono = []
    low = mid = 0.
    for i in range(round(RATE * duration)):
        t = i / RATE
        white = randomizer.uniform(-1, 1)
        low += .042 * (white - low)
        mid += .27 * (white - mid)
        grit = mid - low
        high = white - mid

        def tone(f, sweep=0.0, at=0.0, falloff=0.0):
            d = t - at
            return (sin(TAU * (f * d + sweep * d * d / 2)) * min(1, d * 220)
                    * exp(-d * falloff)) if d > 0 else 0.0

        def tap(at, f, decay=45):
            d = t - at
            return (.43 * tone(f, -90, at, decay) + .60 * grit * min(1, d * 380)
                    * exp(-decay * d)) if d > 0 else 0.0

        if name == 'attack':
            v = .85 * tap(0, 135, 35) + .25 * tone(817, -55, .008, 20) + .14 * tone(1279, 0, .012, 37)
        elif name == 'push':
            v = (grit + .43 * low) * sin(math.pi * t / duration) ** 2 + .60 * tap(.16, 84, 33)
        elif name == 'pickup':
            v = .8 * grit * sin(math.pi * t / duration) ** 2 + .48 * tap(.061, 410) + .40 * tap(.134, 620)
        elif name == 'drop':
            v = 1.05 * tap(.014, 105, 31) + .5 * tap(.071, 75, 25)
        elif name == 'injury':
            v = .43 * tap(0, 105, 28) + .30 * tone(258, -118, .047, 17) + .29 * tone(193, -104, .141, 16)
        elif name == 'objective':
            v = sum(.29 * tone(f, 0, at, 6) + .04 * tone(f * 2, 0, at, 13)
                    for f, at in [(392, 0), (493.88, .105), (587.33, .204)])
        elif name == 'machine_scout':
            v = .31 * tone(106, 890) * (.61 + .39 * sin(TAU * 24 * t)) + .52 * grit * exp(-9 * t)
            v += .28 * tap(.085, 130) + .23 * tap(.164, 177)
        elif name == 'machine_welder':
            v = (1.0 * grit + .49 * high + .14 * tone(98, 50)) * (.16 + .84 * abs(sin(TAU * 5.5 * t)) ** 4)
        elif name == 'machine_hauler':
            v = .31 * tone(57, 40) + .16 * tone(114, 80) + .43 * low
            v += sum(.48 * tap(at, 78, 30) for at in [.025, .127, .238])
        elif name == 'machine_skimmer':
            v = .79 * grit * sin(math.pi * t / duration) + .20 * high * exp(-7 * t)
            v += .26 * tone(230, 1620, .045, 13) + .14 * tone(380, 1110, .082, 16)
        elif name == 'machine_relay':
            v = .8 * tap(.017, 336, 76) + .52 * tap(.077, 554, 80)
            v += (.20 * tone(120, 0, .05, 7) + .065 * tone(240, 0, .05, 10))
        else:
            v = .28 * tone(105, 830) + .13 * tone(210, 1660) + .20 * tone(194, -110, .18, 11)
            v += .55 * tap(.18, 163, 26)
        mono.append(v * envelope(t, duration, .003, .046))
    return write(name, (mono,), .071 if name in ['injury', 'objective'] else .056, .25, design, 'sfx')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tracks = [score(name, *spec) for name, spec in SCORES.items()]
    tracks += [foley(name, duration, 1813 + i, design)
               for i, (name, (duration, design)) in enumerate(FOLEY.items())]
    manifest = {
        'method': 'Project-authored deterministic synthesis. Original pitches and harmonic/filtered-noise synthesis. No voice, sample, external recording or purchased material.',
        'generator': 'tools/generate_audio_nov13.py',
        'assets': tracks,
        'human_listening_accepted': False,
    }
    target = ROOT / 'docs/p4-018-20261113/audio-generated.json'
    target.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
    print(f'Generated {len(tracks)} original audio assets and {target.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
