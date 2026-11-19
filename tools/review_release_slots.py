"""Run the hidden Godot slot recovery regression in a newly named local project."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
ENGINE = ROOT / "work/toolchain/godot-4.7.2/Godot.app/Contents/MacOS/Godot"


def main():
    with tempfile.TemporaryDirectory(prefix="night-tide-slot-review-") as temp:
        review = Path(temp)
        for child in (".godot", "assets", "scenes", "scripts", "data", "tests"):
            source = GAME / child
            if not source.is_dir():
                raise SystemExit(f"Missing {source}. Import the game with the locked Godot engine first.")
            (review / child).symlink_to(source, target_is_directory=True)
        config = (GAME / "project.godot").read_text()
        old = 'config/name="夜潮事务所"'
        if config.count(old) != 1:
            raise SystemExit("Could not assign an independent project name.")
        (review / "project.godot").write_text(config.replace(old, f'config/name="{review.name}"'))
        try:
            args = [
                os.environ.get("GODOT", str(ENGINE)), "--path", str(review),
                "--rendering-method", "gl_compatibility", "--audio-driver", "Dummy",
                "--script", "res://tests/release_slot_recovery.gd",
            ]
            first = subprocess.run(args, timeout=120)
            if first.returncode:
                return first.returncode
            return subprocess.run([*args, "--", "--slot-review-cold"], timeout=120).returncode
        finally:
            marker = review / "slot-review-directory.txt"
            if marker.exists():
                isolated = Path(marker.read_text().strip())
                if isolated.name == review.name and isolated.parent.name == "app_userdata" and isolated.is_dir():
                    shutil.rmtree(isolated)


if __name__ == "__main__":
    raise SystemExit(main())
