"""Audit the 0.18 production clips and optionally export listening reels.

Reads the same paths selected by audio_controller.gd and checks recorded
provenance. Reels are illustrative source mixes, not live-game captures.
"""
from __future__ import annotations

import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import wave

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs/p4-018-20261113'
CONTROLLER = (ROOT / 'game/scripts/presentation/audio_controller.gd').read_text()
BUDGET = {
    'ui': ['ui_focus', 'ui_confirm', 'ui_cancel', 'ui_error', 'ui_page', 'ui_save'],
    'action': ['move', 'attack', 'push', 'stabilize', 'pickup', 'work', 'drop', 'extract'],
    'machine': ['machine_scout', 'machine_welder', 'machine_hauler', 'machine_skimmer',
                'machine_relay', 'machine_sentinel'],
    'alert': ['end_round', 'injury', 'objective', 'ending'],
}
PREVIEW_RATE = 24000


def exact_frames(path):
    with wave.open(str(path), 'rb') as f:
        assert f.getsampwidth() == 2 and f.getnchannels() in [1, 2], path
        pcm = array('h')
        pcm.frombytes(f.readframes(f.getnframes()))
        if sys.byteorder == 'big':
            pcm.byteswap()
        n = f.getnchannels()
        return f.getframerate(), [array('h', pcm[i::n]) for i in range(n)]


def gain_db(level):
    return round(20 * math.log10(max(1 / 32768, level)), 2)


def record(source, name, relpath, category):
    path = ROOT / relpath
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    src, expected = source[relpath]
    assert digest == expected, f'hash changed: {path}'
    rate, channels = exact_frames(path)
    frames = len(channels[0])
    rms = math.sqrt(sum(v * v for ch in channels for v in ch) / (frames * len(channels))) / 32768
    peak = max(max(map(abs, ch)) for ch in channels) / 32768
    assert .012 < rms < .13 and peak < .32, f'outside gain/headroom budget: {path}'
    data = {
        'id': name, 'category': category, 'path': relpath, 'source_receipt': src,
        'sha256': digest, 'rate': rate, 'channels': len(channels),
        'seconds': round(frames / rate, 6), 'rms_dbfs': gain_db(rms), 'peak_dbfs': gain_db(peak),
    }
    if category == 'music':
        jump = max(abs(ch[0] - ch[-1]) for ch in channels)
        # A periodic signal need not be zero at the boundary; compare the
        # join's first difference to the neighbouring samples' slopes.
        seam_residual = max(abs((ch[0] - ch[-1]) - ((ch[1] - ch[0]) + (ch[-1] - ch[-2])) / 2)
                            for ch in channels)
        span = rate // 5
        lead_rms = math.sqrt(sum(v*v for ch in channels for v in ch[:span]) / (span * len(channels)))
        tail_rms = math.sqrt(sum(v*v for ch in channels for v in ch[-span:]) / (span * len(channels)))
        assert frames / rate >= 16 and seam_residual <= 82 and min(lead_rms, tail_rms) > 120, f'loop gap or sample jump: {path}'
        data.update(seam_jump_pcm16=jump, seam_slope_residual_pcm16=seam_residual, seam_head_tail_rms_dbfs=[gain_db(lead_rms / 32768), gain_db(tail_rms / 32768)])
    else:
        assert .04 < frames / rate < .8, f'invalid short cue duration: {path}'
        assert max(abs(ch[-1]) for ch in channels) < 100, f'abrupt release: {path}'
    return data


def build_report():
    source = {}
    for manifest in ['docs/baseline018-audio.json', 'docs/p4-feedback-audio.json',
                     'docs/p4-audio-assets.json', str((DOCS / 'audio-generated.json').relative_to(ROOT))]:
        for entry in json.loads((ROOT / manifest).read_text())['assets']:
            source[entry['path']] = manifest, entry['sha256']

    prefix = re.search(r'const AUDIO_ROOT := "res://([^"]+)"', CONTROLLER)[1]
    music = CONTROLLER.split('const MUSIC := {', 1)[1].split('}', 1)[0]
    loops = [record(source, name, 'game/' + (prefix if operator == 'AUDIO_ROOT + ' else '') + path, 'music')
             for name, operator, path in re.findall(r'"(\w+)": (AUDIO_ROOT \+ )?"(?:res://)?([^"]+)"', music)]
    paths = {}
    for group, directory in [('UI_CUES', 'assets/audio_p4/'), ('OTHER_CUES', 'assets/audio_p4/'),
                             ('NEW_CUES', prefix), ('FIELD_FOLEY', 'assets/audio_feedback/')]:
        declaration = CONTROLLER.split(f'const {group} := [', 1)[1].split(']', 1)[0]
        paths.update({cue: 'game/' + directory + cue + '.wav' for cue in re.findall(r'"(\w+)"', declaration)})
    cues = [record(source, name, paths[name], group) for group, ids in BUDGET.items() for name in ids]
    assert len(loops) == 6 and set(paths) == {row['id'] for row in cues}
    assert len({row['sha256'] for row in cues}) == len(cues) == 24
    return {
        'design': '0.18: release_scope, requirements.AUDIO-01, acceptance.R08',
        'source': 'Original project synthesis; no third-party recordings, voice or model output.',
        'music': loops, 'sfx': cues,
        'metrics': 'Peak, RMS and loop boundaries measured from source PCM, before Godot compression and bus gain.',
        'human_listening_accepted': False,
    }


def stereo_clip(entry):
    rate, channels = exact_frames(ROOT / entry['path'])
    if len(channels) == 1:
        channels *= 2
    count = round(len(channels[0]) * PREVIEW_RATE / rate)
    return [[ch[min(len(ch) - 1, int(i * rate / PREVIEW_RATE))] / 32768 for i in range(count)] for ch in channels]


def silence(seconds):
    return [[0.] * round(seconds * PREVIEW_RATE) for _ in range(2)]


def faded(channels, seconds=.12):
    span = min(round(seconds * PREVIEW_RATE), len(channels[0]) // 2)
    for channel in channels:
        for i in range(span):
            channel[i] *= i / span
            channel[-1 - i] *= i / span
    return channels


def concatenate(chunks):
    return [sum_chunks(chunks, i) for i in range(2)]


def sum_chunks(chunks, channel):
    out = []
    for part in chunks:
        out.extend(part[channel])
    return out


def export_mp3(dest, channels):
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / 'reel.wav'
        with wave.open(str(src), 'wb') as out:
            out.setparams((2, 2, PREVIEW_RATE, 0, 'NONE', ''))
            out.writeframes(array('h', (round(min(.98, max(-.98, s)) * 32767)
                                        for pair in zip(*channels) for s in pair)).tobytes())
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', str(src),
                        '-c:a', 'libmp3lame', '-q:a', '3', str(dest)], check=True)


def previews(report, directory):
    directory.mkdir(parents=True, exist_ok=True)
    music = {e['id']: e for e in report['music']}
    cues = {e['id']: e for e in report['sfx']}
    parts = []
    # One loop seam per 12-second block, at local time 0:05.
    for name in ['camp', 'battle', 'battle_high', 'daily', 'grave', 'ending']:
        clip = stereo_clip(music[name])
        excerpt = [c[-5 * PREVIEW_RATE:] + c[:6 * PREVIEW_RATE] for c in clip]
        parts += [faded(excerpt), silence(1)]
    export_mp3(directory / 'p4-audio-nov13-music.mp3', concatenate(parts))

    parts = []
    # One cue at each integer second, in budget order, at source levels.
    for cue in cues.values():
        clip = stereo_clip(cue)
        parts.append([ch + [0.] * (PREVIEW_RATE - len(ch)) for ch in clip])
    export_mp3(directory / 'p4-audio-nov13-sfx.mp3', concatenate(parts))

    # Example in-game gain ratios. A common 2x gain makes the file easier to
    # preview; the mix retains exactly the Music / Effects slider ratio.
    seconds = 19
    common_gain = 2
    base = stereo_clip(music['battle'])
    high = stereo_clip(music['battle_high'])
    mix = silence(seconds)
    for i in range(len(mix[0])):
        t = i / PREVIEW_RATE
        cross = min(1, max(0, (t - 9) / 1.2))
        for j in range(2):
            mix[j][i] = common_gain * .35 * (base[j][i] * (1 - cross) +
                (high[j][max(0, i - 9 * PREVIEW_RATE)] * cross if cross else 0))
    events = [(1.15, 'move'), (1.37, 'move'), (1.59, 'move'), (2.35, 'stabilize'),
              (3.30, 'pickup'), (4.35, 'work'), (5.1, 'end_round'), (5.58, 'machine_scout'),
              (6.10, 'machine_hauler'), (6.62, 'machine_welder'), (7.14, 'injury'),
              (9.7, 'move'), (9.92, 'move'), (10.72, 'attack'), (11.48, 'push'),
              (12.4, 'machine_relay'), (13.0, 'machine_skimmer'), (13.56, 'machine_sentinel'),
              (15.3, 'extract'), (16.35, 'objective')]
    for when, name in events:
        at = round(PREVIEW_RATE * when)
        for j, ch in enumerate(stereo_clip(cues[name])):
            for i, v in enumerate(ch):
                mix[j][at + i] += common_gain * .60 * v
    export_mp3(directory / 'p4-audio-nov13-field-mix.mp3', faded(mix, .45))


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--previews', type=Path, help='Output directory for three MP3 listening reels (requires FFmpeg)')
    args = cli.parse_args()
    report = build_report()
    (DOCS / 'audio-inventory.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    if args.previews:
        previews(report, args.previews)
    print(f"Audio audit: {len(report['music'])} music loops, {len(report['sfx'])} short cues with verified source hashes")


if __name__ == '__main__':
    main()
