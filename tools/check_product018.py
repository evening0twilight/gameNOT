"""Check the 0.18 alignment without rewriting any historical acceptance evidence."""
import argparse, hashlib, json, os, re, subprocess, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'work/toolchain/godot-4.7.2/Godot.app/Contents/MacOS/Godot'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(args, name):
    start=time.monotonic()
    result=subprocess.run(args,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=1200)
    (ROOT/f'outputs/product018-check-{name}.log').write_text(result.stdout)
    if result.returncode or 'SCRIPT ERROR:' in result.stdout or '\nERROR:' in result.stdout or re.search(r'failures=[1-9]|[1-9][0-9]* failed',result.stdout):
        print(result.stdout);raise SystemExit(f'Failed: {name}')
    markers=[x for x in result.stdout.splitlines() if 'RESULTS:' in x or 'BASELINE018_' in x or 'TEST_RESULTS:' in x]
    print(name+': '+(' | '.join(markers[-2:]) or 'ok'),flush=True)
    return {'name':name,'seconds':round(time.monotonic()-start,2),'markers':markers,'log':f'outputs/product018-check-{name}.log'}
def source_hashes():
    result={str(p.relative_to(ROOT)):digest(p) for base in ['game/scripts','game/scenes','game/data','game/assets'] for p in sorted((ROOT/base).rglob('*')) if p.is_file() and p.suffix not in ['.uid','.import']}
    for name in ['game/project.godot','game/export_presets.cfg']:result[name]=digest(ROOT/name)
    return result
def history_status(allow_missing=False):
    hashes={}
    for filename in ['baseline018-preserved.json','p4-preserved-files.json','p4-feedback-preserved.json','p4-tuning-preserved.json']:
        hashes.update(json.loads((ROOT/'docs'/filename).read_text()))
    missing=[]
    for name,value in hashes.items():
        path=ROOT/name
        optional=(name.startswith('build/') and path.suffix=='.zip') or name in ['outputs/p4-feedback-runtime.avi','outputs/p4-tuning-runtime.avi']
        if not path.is_file():
            if allow_missing and optional:missing.append(name);continue
            raise SystemExit('Historical artifact missing: '+name+' (fresh clones may use --allow-missing-history for excluded ZIP/AVI only)')
        if digest(path)!=value:raise SystemExit('Historical artifact changed: '+name)
    return {'verified':len(hashes)-len(missing),'expected':len(hashes),'missing':missing,'complete':not missing}
def preserved():
    return history_status()['verified']
def main():
    p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');p.add_argument('--allow-missing-history',action='store_true',help='Permit only excluded historical build ZIPs and raw AVI captures; verify every available artifact.');args=p.parse_args()
    history=history_status(args.allow_missing_history)
    if history['missing']:print('Historical artifacts unavailable in this checkout: '+', '.join(history['missing']),flush=True)
    initial_hashes=source_hashes()
    manifest=json.loads((ROOT/'game/data/final_design/design_manifest.json').read_text())
    baseline=json.loads((ROOT/'game/data/final_design'/manifest['authority']).read_text())
    for name,domain in manifest['generated_views'].items():
        assert json.loads((ROOT/name).read_text())==baseline['domains'][domain],name
    locked=json.loads((ROOT/'tools/toolchain.lock.json').read_text())
    engine=os.environ.get('GODOT',str(ENGINE))
    assert subprocess.check_output([engine,'--version'],text=True).strip()==locked['godot']['version_output']
    game_files={str(p.relative_to(ROOT/'game')).casefold():p for p in (ROOT/'game').rglob('*') if p.is_file() and '.godot' not in p.parts}
    for path in (ROOT/'game/scripts').rglob('*.gd'):
        for reference in re.findall(r'(?:preload|load)\("res://([^"%]+)"\)',path.read_text()):assert reference.casefold() in game_files,(path,reference)
    records=[run([engine,'--headless','--path','game','--editor','--import','--quit'],'import')]
    names=['run_tests','content_catalog_tests','p1_tests','p1_systems_tests','p3_rules_tests','p3_specialties_tests','p3_story_proofs','p4_history_tests','p4_tests','p4_feedback_tests','baseline018_tests','baseline018_edges','baseline018_guidance','ui_localization_tests','baseline018_ui','product018_story_tests']
    for name in names:records.append(run([engine,'--headless','--path','game','--script',f'tests/{name}.gd','--','--isolated-ui-review'],name))
    if args.full:
        for name in ['baseline018_missions','baseline018_field_paths','baseline018_campaign','baseline018_linked_campaign','product018_crew_campaign']:
            records.append(run([engine,'--headless','--path','game','--script',f'tests/{name}.gd'],name))
        for difficulty in ['relaxed','standard','hard']:
            records.append(run([engine,'--headless','--path','game','--script','tests/baseline018_matrix.gd','--','--difficulty='+difficulty],'matrix-'+difficulty))
        for profile in ['no_training','few_sides','fixed_favorites','injury_rotation']:
            records.append(run([engine,'--headless','--path','game','--script','tests/baseline018_profiles.gd','--','--profile='+profile],'profile-'+profile))
    assert initial_hashes==source_hashes(),'Game sources changed during validation; rerun against one consistent revision'
    history=history_status(args.allow_missing_history)
    record={'authority':manifest['version'],'full':args.full,'checks':records,'preserved_files':history['verified'],'history':history,'source_hashes':initial_hashes,'windows_native_tested':False,'human_acceptance':False}
    (ROOT/'outputs/product018-checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print('BASELINE018_CHECK_OK: implementation checks; Windows native and human acceptance remain separate')
if __name__=='__main__':main()
