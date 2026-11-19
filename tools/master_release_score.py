"""Render the six instrumental cues offline from retained sources and fixed edit points.

Requires FFmpeg, NumPy and SciPy. The game uses only the resulting WAV resources.
"""
import hashlib
import json
import re
import struct
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, resample_poly, sosfilt

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/p4-release-20261119"
ASSETS = ROOT / "game/assets/product018/audio/score"
SOURCES = ROOT / "outputs/p4release-20261119/audio-sources"
RATE = 32000
# The opening is played once. Endings overlap music just before the loop head.
# Times are seconds at the source rate. Level is LUFS before the music bus.
EDITS = {
    "camp": (10.96, 36.46, .76, -28.5),
    "battle": (7.38, 34.84, .48, -27.5),
    "battle_high": (9.82, 42.08, .48, -26.5),
    "daily": (11.92, 37.14, .45, -28.5),
    "grave": (1.78, 27.12, .70, -29.0),
    "ending": (11.98, 40.54, .90, -27.5),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measure(path):
    result = subprocess.run(
        ["ffmpeg", "-nostdin", "-hide_banner", "-i", str(path), "-af", "ebur128=peak=true",
         "-f", "null", "-"], check=True, capture_output=True, text=True)
    summary = result.stderr.rsplit("Summary:", 1)[-1]
    return {name: float(re.search(pattern, summary)[1]) for name, pattern in {
        "lufs": r"I:\s+([-\d.]+) LUFS",
        "true_peak_dbfs": r"Peak:\s+([-\d.]+) dBFS",
        "range_lu": r"LRA:\s+([-\d.]+) LU",
    }.items()}


def reconstruct_rails(samples):
    # Estimate only the few samples pinned at a 16-bit rail. Match both value
    # and local slope at the neighbours, leaving every other sample untouched.
    count = 0
    for channel in samples.T:
        rails = (channel >= 32767) | (channel <= -32768)
        edges = np.flatnonzero(np.diff(np.r_[False, rails, False]))
        for start, stop in edges.reshape(-1, 2):
            if start < 2 or stop > len(channel) - 2 or stop - start > 96:
                raise ValueError("Clipped passage requires another edit")
            count += stop - start
            span = stop - start + 1
            t = np.arange(1, span) / span
            left, right = channel[start - 1], channel[stop]
            m1 = span * (left - channel[start - 2])
            m2 = span * (channel[stop + 1] - right)
            channel[start:stop] = ((2*t**3 - 3*t**2 + 1)*left + (t**3 - 2*t**2 + t)*m1
                                   + (-2*t**3 + 3*t**2)*right + (t**3 - t**2)*m2)
    return int(count)


def render(name, start, stop, overlap, target):
    source = SOURCES / (name + ".flac")
    decoded = subprocess.check_output(["ffmpeg", "-nostdin", "-v", "error", "-i", str(source),
                                       "-ac", "2", "-ar", "48000", "-f", "s16le", "-"])
    samples = np.frombuffer(decoded, dtype="<i2").reshape(-1, 2)
    section = samples[:round(stop * 48000)].astype(np.float64)
    repaired = reconstruct_rails(section)
    # Include source context for the resampler at the endpoint before trimming.
    context = samples[len(section):len(section) + 128]
    pcm = resample_poly(np.vstack([section, context]) / 32768, 2, 3, axis=0)[:round(stop * RATE)]
    if name == "grave":
        # The first arrangement's high fiddle and rapid attacks dominated the
        # letter scene. Lower the register and lengthen each bow in this cue.
        low = sosfilt(butter(2, 1500, fs=RATE, output="sos"), pcm, axis=0)
        pcm = resample_poly(.68 * pcm + .32 * low, 7, 5, axis=0)
    head = round(start * RATE * (1.4 if name == "grave" else 1.0))
    fade = round(overlap * RATE)
    theta = np.linspace(0, np.pi/2, fade)[:, None]
    pcm[-fade:] = pcm[-fade:] * np.cos(theta) + pcm[head-fade:head] * np.sin(theta)
    if name == "daily":
        # The generation closes the first phrase to silence, then starts a
        # second take. Overlap its quiet decay with the next phrase's pickup.
        first_end = round(20.44 * RATE)
        second_start = round(21.12 * RATE)
        join = round(.72 * RATE)
        blend = np.linspace(0, np.pi/2, join)[:, None]
        bridge = pcm[first_end-join:first_end]*np.cos(blend) + pcm[second_start:second_start+join]*np.sin(blend)
        pcm = np.vstack([pcm[:first_end-join], bridge, pcm[second_start+join:]])
    out = ASSETS / (name + ".wav")
    with tempfile.TemporaryDirectory() as tmp:
        floating = Path(tmp) / "floating.wav"
        wavfile.write(floating, RATE, pcm.astype(np.float32))
        measured = measure(floating)
    gain = min(target - measured["lufs"], -11 - measured["true_peak_dbfs"])
    pcm16 = np.rint(pcm * (32767 * 10**(gain/20))).astype("<i2")
    wavfile.write(out, RATE, pcm16)
    # Portable RIFF sampler loop. WAV stores the last included frame index.
    payload = struct.pack("<15I", 0, 0, round(1e9/RATE), 60, 0, 0, 0, 1, 0,
                          0, 0, head, len(pcm16) - 1, 0, 0)
    data = bytearray(out.read_bytes() + b"smpl" + struct.pack("<I", len(payload)) + payload)
    data[4:8] = struct.pack("<I", len(data) - 8)
    out.write_bytes(data)
    return {
        "id": name, "kind": "music", "path": str(out.relative_to(ROOT)), "sha256": sha(out),
        "source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
        "decoded_source_pcm_sha256": hashlib.sha256(decoded).hexdigest(),
        "sample_rate": RATE, "channels": 2, "intro_seconds": head / RATE, "seconds": len(pcm16) / RATE, "source_end_seconds": stop,
        "loop_seconds": round((len(pcm16) - head) / RATE, 3), "loop_begin_frame": head, "frames": len(pcm16),
        "overlap_seconds": overlap, "gain_db": round(gain, 2), "reconstructed_rail_samples": repaired,
        "seam_step_pcm16": max(abs(int(pcm16[head,i])-int(pcm16[-1,i])) for i in (0,1)),
        "seam_slope_residual_pcm16": max(abs(int(pcm16[head,i])-int(pcm16[-1,i]) -
              .5 * (int(pcm16[head+1,i])-int(pcm16[head,i])+int(pcm16[-1,i])-int(pcm16[-2,i]))) for i in (0,1)),
        **measure(out),
    }


if __name__ == "__main__":
    ASSETS.mkdir(parents=True, exist_ok=True)
    rows = [render(name, *params) for name, params in EDITS.items()]
    (DOCS / "audio-generated.json").write_text(json.dumps({
        "method": "Instrumental recordings generated through the Model Studio audio inference API, then edited and mastered offline. Retained lossless sources and edit parameters.",
        "tool": "tools/master_release_score.py", "assets": rows, "human_listening_accepted": False,
    }, indent=2, ensure_ascii=False) + "\n")
    print([(r["id"], r["loop_seconds"], r["lufs"]) for r in rows])
