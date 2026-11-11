"""Development checks, independent of the frozen review's runtime-unchanged gate."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from evidence import restore

ROOT = Path(__file__).resolve().parents[1]

def run(args, marker=None, env=None):
    result = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, timeout=int(os.environ.get("NIGHT_TIDE_CHECK_TIMEOUT", "180")))
    print(result.stdout, end='', flush=True)
    if result.returncode or 'SCRIPT ERROR:' in result.stdout or '\nERROR:' in result.stdout:
        raise SystemExit(result.returncode or 1)
    if marker and marker not in result.stdout:
        raise SystemExit(f'Missing success marker: {marker}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--engine', action='store_true')
    args = parser.parse_args()
    run([sys.executable, "tools/check_repository.py"], "REPOSITORY_OK:")
    restore()
    manifest = json.loads((ROOT / 'game/data/final_design/design_manifest.json').read_text())
    base = json.loads((ROOT / 'game/data/final_design' / manifest['authority']).read_text())
    if base['version'] != manifest['version']:
        raise SystemExit('Design version mismatch')
    for path, domain in manifest['generated_views'].items():
        if json.loads((ROOT / path).read_text()) != base['domains'][domain]:
            raise SystemExit(f'Stale generated view: {path}')
    print(f'DESIGN_VIEWS_OK: {len(manifest["generated_views"])}')
    run([sys.executable, 'work/predevelopment-review/regression.py'], 'RULE CHECKS 1172', env={**os.environ, 'NIGHT_TIDE_CURRENT_RULE_CHECK': '1'})
    print('HISTORICAL_GATES_EXCLUDED: 2 runtime byte-identity assertions; original hashes preserved')
    if args.engine:
        lock = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
        engine = os.environ.get('GODOT', str(ROOT / lock['godot']['local_macos_binary']))
        version = subprocess.check_output([engine, '--version'], text=True).strip()
        if version != lock['godot']['version_output']:
            raise SystemExit(f'Engine version mismatch: {version}')
        run([engine, '--headless', '--path', 'game', '--editor', '--import', '--quit'])
        run([engine, '--headless', '--path', 'game', '--script', 'tests/run_tests.gd'], 'TEST_RESULTS:')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/content_catalog_tests.gd'], 'CONTENT_TEST_RESULTS: failures=0')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/p1_tests.gd'], 'P1_TEST_RESULTS:')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/p1_systems_tests.gd'], 'P1_SYSTEMS_RESULTS:')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/ui_localization_tests.gd'], 'UI_LOCALIZATION_RESULTS:')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/visual_p1_tests.gd'], 'VISUAL_P1_RESULTS:')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/chapter_one_tests.gd'], 'CHAPTER_ONE_RESULTS:')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/full_playthrough.gd'], 'P3_PATH_RESULTS:')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/p3_rules_tests.gd'], 'P3_RULES_RESULTS:')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/p3_specialties_tests.gd'], 'P3_SPECIALTIES_RESULTS:')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/p3_story_proofs.gd'], 'P3_STORY_PROOFS_RESULTS:')
        campaigns = []
        for mode in ['shared_control', 'distributed_rebuild', 'evacuation', 'failure']:
            run([engine, '--headless', '--path', 'game', '--script', 'tests/campaign_playthrough.gd', '--', '--campaign-mode=' + mode], 'P3_CAMPAIGN_RESULTS: campaigns=1 failures=0')
            campaigns.extend(json.loads((ROOT / ('outputs/p4-tuning-campaign-paths-' + mode + '.json')).read_text()))
        (ROOT / 'outputs/p4-tuning-campaign-paths.json').write_text(json.dumps(campaigns, ensure_ascii=False, indent=2) + '\n')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/p2_presentation_tests.gd'], 'P2_PRESENTATION_RESULTS:')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/p3_presentation_tests.gd'], 'P3_PRESENTATION_RESULTS:')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/p4_tests.gd'], 'P4_PRODUCT_RESULTS:')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/p4_history_tests.gd'], 'P4_HISTORY_RESULTS:')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/p4_presentation_tests.gd'], 'P4_PRESENTATION_RESULTS:')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/p4_feedback_tests.gd'], 'P4_FEEDBACK_RESULTS:')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/p4_tuning_tests.gd'], 'P4_TUNING_RESULTS:')
        run([engine, '--headless', '--path', 'game', '--script', 'tests/p4_hard_route_probe.gd'], 'P4_HARD_ROUTE_RESULTS: paths=2 failures=0')
        for profile in ['no_training', 'few_sides', 'fixed_favorites', 'injury_rotation']:
            run([engine, '--headless', '--path', 'game', '--script', 'tests/p4_campaign_profiles.gd', '--', '--profile=' + profile], 'P4_PROFILE_RESULTS:')
        for difficulty in ['relaxed', 'standard', 'hard']:
            run([engine, '--headless', '--path', 'game', '--script', 'tests/p4_matrix.gd', '--', '--difficulty=' + difficulty], 'P4_MATRIX_RESULTS: paths=72 failures=0')
        run([engine, '--headless', '--path', 'game', '--quit-after', '3'], 'PROJECT_BOOT_OK:')
    print('CHECK_OK: current development automated checks; P4 Windows native acceptance remains separate')

if __name__ == '__main__':
    main()
