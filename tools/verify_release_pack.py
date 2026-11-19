"""Read the delivered Windows ZIP and run probes against its PCK from an empty project."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import struct
import subprocess
import sys
import tempfile
import zipfile

from check_product018 import ENGINE, ROOT, digest, source_hashes


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def credential_values():
    path = ROOT / ".env"
    values = []
    if path.is_file():
        for line in path.read_text().splitlines():
            key, delimiter, value = line.partition("=")
            if delimiter and not key.lstrip().startswith("#") and re.search(
                r"api.?key|secret|token|password|SFM_WORKSPACE_ID", key, re.I
            ):
                value = value.strip().strip("\"'")
                if len(value) >= 12:
                    values.append(value.encode("utf-8"))
    return values


def safe_name(name):
    parts = PurePosixPath(name).parts
    return (bool(parts) and not name.startswith("/") and ".." not in parts
            and "\\" not in name and ":" not in name
            and all(not x.casefold().startswith((".env", ".git")) for x in parts))


def inspect_pck(data, hashes):
    """The pinned engine exports unencrypted, uncompressed v4 PCK directory tables."""
    magic, version, major, minor, patch, flags, base, directory = struct.unpack_from("<4s5I2Q", data)
    require((magic, version, major, minor, patch, flags) == (b"GDPC", 4, 4, 7, 2, 2), "Unexpected PCK header")
    require(0 < base < directory < len(data), "Invalid PCK directory location")
    count, = struct.unpack_from("<I", data, directory)
    position = directory + 4
    packaged_data = {}
    paths = set()
    engine_entries = {}
    referenced_resources = set()
    view = memoryview(data)
    for _ in range(count):
        length, = struct.unpack_from("<I", data, position)
        position += 4
        name = data[position:position + length].rstrip(b"\0").decode("utf-8")
        position += length
        offset, size, md5, file_flags = struct.unpack_from("<QQ16sI", data, position)
        position += 36
        require(safe_name(name) and name not in paths, "Unsafe or duplicate PCK path")
        paths.add(name)
        start = base + offset
        require(file_flags == 0 and base <= start <= start + size <= directory, f"Invalid PCK member {name}")
        blob = view[start:start + size]
        require(hashlib.md5(blob).digest() == md5, f"PCK entry checksum: {name}")
        # Godot ships its compiled resources, import maps, and UID/class lookup
        # tables under .godot/. Editor metadata and developer caches are excluded.
        if name.startswith(".godot/"):
            part = "/".join(name.split("/")[:2])
            require(part in {".godot/imported", ".godot/exported", ".godot/uid_cache.bin",
                             ".godot/global_script_class_cache.cfg"}, f"Editor-local PCK path: {name}")
            engine_entries[part] = engine_entries.get(part, 0) + 1
        elif name.startswith(("assets/", "scenes/")):
            source = "game/" + name.removesuffix(".remap").removesuffix(".import")
            require(source in hashes, f"Asset/scene not in checked source: {name}")
            if name.endswith((".import", ".remap")):
                refs = re.findall(rb'^path(?:\.\w+)?="res://(\.godot/[^"]+)"', blob, re.M)
                require(refs, f"Exported resource map has no target: {name}")
                referenced_resources.update(r.decode("utf-8") for r in refs)
            else:
                require(hashlib.sha256(blob).hexdigest() == hashes[source], f"Raw asset copy differs: {name}")
        elif name.startswith("data/"):
            key = "game/" + name
            require(key in hashes and name.endswith(".json"), f"Untracked PCK data: {name}")
            actual = hashlib.sha256(blob).hexdigest()
            require(actual == hashes[key], f"Exported data differs from checked source: {name}")
            packaged_data[key] = actual
        else:
            require(name == "project.binary" or name.startswith(("assets/", "scenes/", "scripts/")),
                    f"Unexpected PCK content root: {name}")
            require(not any(part.casefold() in {"profiles", "cache", "local storage", "user data", "tests", ".git"}
                            for part in PurePosixPath(name).parts), f"Local material in PCK: {name}")
    require({p for p in paths if p.startswith((".godot/imported/", ".godot/exported/"))} == referenced_resources,
            "Exported binary resources must match the runtime import map references")
    require(position == len(data), "Unexpected bytes following the PCK directory")
    require(set(packaged_data) == {k for k in hashes if k.startswith("game/data/") and k.endswith(".json")},
            "Not all checked game data made it into the archive")
    scripts = {p.removeprefix("game/").removesuffix(".gd") for p in hashes if p.startswith("game/scripts/") and p.endswith(".gd")}
    require({p for p in paths if p.startswith("scripts/")} ==
            {stem + ext for stem in scripts for ext in [".gdc", ".gd.remap"]},
            "Compiled production scripts/remaps do not match the checked runtime script list")
    return {"members": count, "compiled_scripts": len(scripts), "remap_targets": len(referenced_resources), "data_sha256": packaged_data,
            "engine_runtime_resource_entries": engine_entries,
            "directory_checksums_verified": count, "editor_cache_or_test_roots": []}


def run_engine(engine, empty, pack, script, args):
    command = [engine, "--headless", "--audio-driver", "Dummy", "--path", str(empty),
               "--main-pack", str(pack), "--script", str(script), "--", *map(str, args)]
    result = subprocess.run(command, cwd=empty, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=200)
    require(result.returncode == 0 and "SCRIPT ERROR:" not in result.stdout and "\nERROR:" not in result.stdout,
            f"{script.name} failed: {result.stdout[-1800:]}")
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", default="p4release-20261119")
    parser.add_argument("--review-dir", type=Path, default=ROOT / "docs/p4-release-20261119")
    args = parser.parse_args()
    prefix = args.candidate
    require(re.fullmatch(r"[a-z0-9][a-z0-9-]*", prefix), "Invalid candidate label")
    review = args.review_dir.resolve()
    build = read_json(ROOT / f"docs/{prefix}-build.json")
    checks = read_json(ROOT / f"outputs/{prefix}-checks.json")
    archive = ROOT / build["package"]
    supply = ROOT / f"outputs/{prefix}"
    require(checks["full"] and checks["source_hashes"] == build["build"]["source_hashes"] == source_hashes(),
            "Candidate receipt, full checks and fixed game sources disagree")
    require(archive.stat().st_size == build["bytes"] and digest(archive) == build["sha256"],
            "Input ZIP does not match its candidate receipt")
    story_evidence = read_json(review / "story-evidence.json")
    source_map_digest = hashlib.sha256(json.dumps(checks["source_hashes"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    require(story_evidence["gpu_fixed_source"]["sha256"] == source_map_digest, "Story captures differ from fixed candidate sources")
    for path, expected in story_evidence["sha256"].items():
        require(digest(ROOT/path) == expected, f"Story review input or capture changed: {path}")
    owned_secrets = credential_values()
    engine = os.environ.get("GODOT", str(ENGINE))
    archives = {}
    with tempfile.TemporaryDirectory(prefix="night-tide-verify-") as temp:
        work = Path(temp)
        empty = work / "empty-project"
        empty.mkdir()
        with zipfile.ZipFile(archive) as z:
            names = z.namelist()
            require(all(safe_name(n) for n in names) and len(names) == len(set(names)), "Invalid archive member")
            executable = z.read("night-tide.exe")
            pe_offset, = struct.unpack_from("<I", executable, 0x3c)
            require(executable[:2] == b"MZ" and executable[pe_offset:pe_offset+6] == b"PE\0\0\x64\x86", "Missing x86-64 PE header")
            require(z.testzip() is None, "ZIP CRC check failed")
            permissions = {"Godot-LICENSE.txt": ROOT/"docs/baseline018-engine-license.txt",
                           "OFL.txt": ROOT/"game/assets/fonts/OFL.txt",
                           "asset-sources.csv": ROOT/"docs/asset-register.csv",
                           "audio-generated.json": review/"audio-generated.json",
                           "audio-inventory.json": review/"audio-inventory.json"}
            player_files = {"FIELD-GUIDE.txt": review/"guide.txt",
                            "REFERENCE-SESSION.md": review/"reference-session.md",
                            "playtest-form.csv": review/"playtest-form.csv",
                            "Record-Windows-Session.cmd": ROOT/"tools/Record-Windows-Session.cmd",
                            "Record-Windows-Session.ps1": ROOT/"tools/Record-Windows-Session.ps1",
                            "Run-Windows-Checks.cmd": ROOT/"tools/windows_acceptance_baseline018.cmd"}
            for name, source in player_files.items():
                require(z.read(name) == source.read_bytes(), f"Player/reviewer handout differs: {name}")
            require(z.read("README.txt").decode("utf-8").endswith((review/"start.txt").read_text()),
                    "Quick-start text differs from the trilingual release guide")
            local_links = []
            for name in ("PRODUCT-REVIEW.md", "THIS-BUILD-REVIEW.md", "REFERENCE-SESSION.md"):
                for target in re.findall(r"\]\(([^)#]+)\)", z.read(name).decode("utf-8")):
                    if "://" in target:
                        continue
                    require(target in names, f"Broken packaged reference in {name}: {target}")
                    local_links.append({"document": name, "target": target})
            for name, source in permissions.items():
                require(z.read(name) == source.read_bytes(), f"License or provenance copy differs: {name}")
            for name in names:
                require(re.fullmatch(r"(?:review-images/[A-Za-z0-9_-]+\.png|[A-Za-z0-9_-]+\.(?:exe|pck|json|txt|csv|md|cmd|ps1))", name),
                        f"Unexpected loose file in release ZIP: {name}")
                payload = z.read(name)
                require(not any(secret in payload for secret in owned_secrets), f"Configured credential present in {name}")
                archives[name] = hashlib.sha256(payload).hexdigest()
            require(json.loads(z.read("build-receipt.json")) == build["build"], "ZIP's embedded build receipt differs")
            for name in ("night-tide.exe", "night-tide.pck"):
                require(archives[name] == build["build"]["sha256"][name], "Executable/pack differs from receipt")
            pack = work / "night-tide.pck"
            packed = z.read("night-tide.pck")
            pack_report = inspect_pck(packed, checks["source_hashes"])
            pack.write_bytes(packed)
        source_scripts = [p for p in checks["source_hashes"] if p.startswith("game/scripts/") and p.endswith(".gd")]
        for source in source_scripts:
            text = (ROOT / source).read_text()
            require(not re.search(r"\b(?:HTTPClient|HTTPRequest|WebSocketPeer|WebRTCPeerConnection)\b|aliyun-apikey|SFM_WORKSPACE_ID", text),
                    f"Remote API primitive or configured service identifier in checked runtime: {source}")
            require(not any(s in text.encode("utf-8") for s in owned_secrets), f"Configured credential in checked runtime {source}")
        language_out = run_engine(engine, empty, pack, ROOT/"tools/verify_pack_languages.gd", [])
        lang = json.loads(next(line.removeprefix("PACKAGED_LANGUAGES: ") for line in language_out.splitlines()
                               if line.startswith("PACKAGED_LANGUAGES: ")))
        for locale, result in lang.items():
            require(result["sha256"] == checks["source_hashes"][f"game/data/localization/{locale}.json"], "Pack language mismatch")
        runtime_path = work/"campaign.json"
        run_engine(engine, empty, pack, ROOT/"tools/verify_release_pack.gd", [supply, runtime_path])
        runtime = read_json(runtime_path)
        require(runtime["problems"] == [] and runtime["authority"] == checks["source_hashes"]["game/data/final_design/release_baseline.json"], "Runtime authority mismatch")
        for profile in ["main","sides","recovery"]:
            history = read_json(supply/f"learning-{profile}.json")
            require(history["failures"] == [], "Continuous source run failed")
            for c in history["checkpoints"]:
                key = Path(c["file"]).stem
                if key in runtime["saves"]:
                    require(c["sha256"] == runtime["saves"][key]["sha256"], "Save differs from continuous command receipt")
        score_path = work/"score.json"
        run_engine(engine, empty, pack, ROOT/"game/tests/release_score_review.gd", [score_path, "--packaged"])
        score = read_json(score_path)
        require(score["passed"] and score["packaged"] and not score["retired_music_present"] and
                len(score["short_cues_present"]) == 24, "Pack score probe failed")
        write_json(review/"packaged-score.json", score)
    report = {"candidate": prefix, "runtime": f"{sys.platform} headless, extracted ZIP/PCK in an empty project; dummy audio output",
              "windows_native_tested": False, "human_acceptance": False, "zip_sha256":build["sha256"],
              "zip_bytes":build["bytes"], "pe_machine":"AMD64", "zip_members_sha256":archives,
              "verified_handouts":list(player_files)+["README.txt"], "verified_handout_links":local_links,
              "license_and_provenance_copies":list(permissions), "pack":pack_report,"locales":lang,
              "story_capture_source_map_sha256":source_map_digest,
              "campaigns":runtime, "packaged_score":"packaged-score.json",
              "packaged_score_sha256":digest(review/"packaged-score.json"),
              "credential_scan":{"configured_values_compared":len(owned_secrets), "matches":0,
                                 "runtime_script_files_checked":len(source_scripts),
                                 "scope":"Exact locally configured credentials (12+ characters), checked against ZIP member bytes and runtime script source. No network client class or configured service identifier in checked runtime. Compiled resources and runtime UID/class lookups are expected under .godot/. No claim concerning arbitrary unknown keys."}}
    write_json(review/"packaged-checks.json",report)
    print(f"RELEASE_PACKAGE_VERIFIED {build['sha256']}  {len(archives)} ZIP entries, {pack_report['members']} PCK members")


if __name__ == "__main__":
    main()
