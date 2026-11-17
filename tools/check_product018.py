"""Check the 0.18 alignment without rewriting any historical acceptance evidence."""
import functools
from concurrent.futures import ThreadPoolExecutor
import argparse, hashlib, json, os, re, subprocess, time, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'work/toolchain/godot-4.7.2/Godot.app/Contents/MacOS/Godot'
RETIREMENTS='docs/product018-history-retirements.json'
TUTORIAL_AMENDMENT='docs/p4-firstshift-20261117/tutorial-amendment.json'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(args, name, prefix="product018"):
    start=time.monotonic()
    result=subprocess.run(args,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=1200)
    (ROOT/f'outputs/{prefix}-check-{name}.log').write_text(result.stdout)
    if result.returncode or 'SCRIPT ERROR:' in result.stdout or '\nERROR:' in result.stdout or re.search(r'failures=[1-9]|[1-9][0-9]* failed',result.stdout):
        print(result.stdout);raise SystemExit(f'Failed: {name}')
    markers=[x for x in result.stdout.splitlines() if 'RESULTS:' in x or 'BASELINE018_' in x or 'TEST_RESULTS:' in x or 'P4_AUDIO_NOV13:' in x]
    print(name+': '+(' | '.join(markers[-2:]) or 'ok'),flush=True)
    return {'name':name,'seconds':round(time.monotonic()-start,2),'markers':markers,'log':f'outputs/{prefix}-check-{name}.log'}
def source_hashes():
    result={str(p.relative_to(ROOT)):digest(p) for base in ['game/scripts','game/scenes','game/data','game/assets'] for p in sorted((ROOT/base).rglob('*')) if p.is_file() and p.suffix not in ['.uid','.import']}
    for name in ['game/project.godot','game/export_presets.cfg']:result[name]=digest(ROOT/name)
    return result
def excluded_history(name):
    return (name.startswith('build/') and name.endswith('.zip')) or name in [
        'outputs/p4-feedback-runtime.avi','outputs/p4-tuning-runtime.avi']

def history_status(allow_missing=False):
    hashes={}
    for filename in ['baseline018-preserved.json','p4-preserved-files.json','p4-feedback-preserved.json','p4-tuning-preserved.json']:
        hashes.update(json.loads((ROOT/'docs'/filename).read_text()))
    policy=json.loads((ROOT/RETIREMENTS).read_text())
    discarded=policy['discarded']
    duplicates=policy['duplicate_captures']
    for name,value in discarded.items():
        if not excluded_history(name) or name not in hashes or hashes[name]!=value:
            raise SystemExit('Invalid historical artifact retirement: '+name)
    for name,replacement in duplicates.items():
        directory,_,leaf=name.rpartition('/')
        retained_dir={'outputs/p3-gui':'outputs/p4-gui','outputs/p4-feedback-gui':'outputs/p4-tuning-gui'}.get(directory)
        if not retained_dir or not leaf.endswith('.png') or replacement!=f'{retained_dir}/{leaf}':
            raise SystemExit('Invalid historical duplicate capture: '+name)
        if name in hashes and hashes.get(replacement)!=hashes[name]:
            raise SystemExit('Historical duplicate has no protected replacement: '+name)
    amended={}
    amendment=ROOT/TUTORIAL_AMENDMENT
    if amendment.is_file():
        decision=json.loads(amendment.read_text())
        expected={'game/data/final_design/release_baseline.json','game/data/final_design/player_experience_contract.json'}
        if set(decision['paths'])!=expected or decision['changed_fields']!=['schedule','not_railroad','automatic_budget']:
            raise SystemExit('Invalid tutorial amendment scope')
        for name,record in decision['paths'].items():
            archive=ROOT/record['archive'];current=ROOT/name
            if not record['archive'].startswith('docs/p4-firstshift-20261117/before-') or not archive.is_file() or not current.is_file():
                raise SystemExit('Missing tutorial amendment evidence: '+name)
            if (name in hashes and record['before_sha256']!=hashes[name]) or digest(archive)!=record['before_sha256'] or digest(current)!=record['after_sha256']:
                raise SystemExit('Tutorial amendment hash mismatch: '+name)
            before=json.loads(archive.read_text());after=json.loads(current.read_text())
            old=before['domains']['experience'] if name.endswith('release_baseline.json') else before
            new=after['domains']['experience'] if name.endswith('release_baseline.json') else after
            for field in decision['changed_fields']:
                new['tutorial_policy'][field]=old['tutorial_policy'][field]
            if before!=after:raise SystemExit('Tutorial amendment changed unrelated design: '+name)
            if name in hashes:amended[name]=record['archive']
    missing=[]
    retired=[]
    for name,value in hashes.items():
        path=ROOT/name
        if path.is_file():
            if digest(path)!=value and name not in amended:raise SystemExit('Historical artifact changed: '+name)
        elif path.exists() or path.is_symlink():
            raise SystemExit('Historical artifact is not a file: '+name)
        elif name in discarded or name in duplicates:
            retired.append(name)
        elif allow_missing and excluded_history(name):
            missing.append(name)
        else:
            raise SystemExit('Historical artifact missing: '+name+' (--allow-missing-history permits only excluded ZIP/AVI)')
    result={'verified':len(hashes)-len(missing)-len(retired),'expected':len(hashes),
            'missing':sorted(missing),'retired':sorted(retired),'complete':not (missing or retired)}
    if amended:result.update({'amended_originals_verified_at':amended,'unchanged_original_paths':result['verified']-len(amended)})
    return result
def preserved():
    return history_status()['verified']
def main():
    p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');p.add_argument('--jobs',type=int,choices=range(1,5),default=1,help='Parallel independent full-campaign checks; default 1 for modest machines.');p.add_argument('--allow-missing-history',action='store_true',help='Permit missing excluded historical build ZIPs and raw AVI captures beyond recorded retirements.');p.add_argument('--report-prefix',default='product018');args=p.parse_args()
    assert re.fullmatch(r'[a-z0-9][a-z0-9-]*',args.report_prefix),'Invalid report prefix'
    execute=functools.partial(run,prefix=args.report_prefix)
    history=history_status(args.allow_missing_history)
    print(f"Historical artifact paths verified: {history['verified']}/{history['expected']}; "
          f"retired: {len(history['retired'])}; otherwise unavailable: {len(history['missing'])}",flush=True)
    if history['missing']:print('Historical artifacts unavailable in this checkout: '+', '.join(history['missing']),flush=True)
    if history.get('amended_originals_verified_at'):print('User-authorized tutorial amendment; originals verified at archived paths: '+json.dumps(history['amended_originals_verified_at']),flush=True)
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
    records=[execute([engine,'--headless','--path','game','--editor','--import','--quit'],'import')]
    names=['run_tests','content_catalog_tests','p1_tests','p1_systems_tests','p3_rules_tests','p3_specialties_tests','p3_story_proofs','p4_history_tests','p4_tests','p4_feedback_tests','baseline018_tests','baseline018_edges','baseline018_guidance','ui_localization_tests','baseline018_ui','product018_story_tests','p4close_tests','p4quality_tests','firstshift_review','fieldguide_review','campguide_review','multilanguage_review','language_lategame_review']
    for name in names:records.append(execute([engine,'--headless','--path','game','--script',f'tests/{name}.gd','--','--isolated-ui-review'],name))
    records.append(execute([sys.executable,'tools/check_localization.py'],'language_catalog'))
    records.append(execute([engine,'--headless','--path','game','--script','tests/p4_audio_nov13.gd','--',str(ROOT/'outputs/baseline018-linked-day24.json')],'p4_audio_nov13'))
    if args.full:
        # These rule-only processes write distinct reports and unique save slots.
        # UI/import checks stay sequential; none of these jobs consumes another's output.
        jobs=[]
        for name in ['baseline018_missions','baseline018_field_paths','baseline018_campaign','baseline018_linked_campaign','product018_crew_campaign','p4close_growth_campaign']:
            jobs.append(([engine,'--headless','--path','game','--script',f'tests/{name}.gd'],name))
        for difficulty in ['relaxed','standard','hard']:
            jobs.append(([engine,'--headless','--path','game','--script','tests/baseline018_matrix.gd','--','--difficulty='+difficulty],'matrix-'+difficulty))
        for profile in ['no_training','few_sides','fixed_favorites','injury_rotation']:
            jobs.append(([engine,'--headless','--path','game','--script','tests/baseline018_profiles.gd','--','--profile='+profile],'profile-'+profile))
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            records.extend(pool.map(lambda job:execute(*job),jobs))
    assert initial_hashes==source_hashes(),'Game sources changed during validation; rerun against one consistent revision'
    history=history_status(args.allow_missing_history)
    record={'authority':manifest['version'],'full':args.full,'jobs':args.jobs,'checks':records,'preserved_files':history['verified'],'history':history,'source_hashes':initial_hashes,'windows_native_tested':False,'human_acceptance':False}
    (ROOT/f'outputs/{args.report_prefix}-checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print('BASELINE018_CHECK_OK: implementation checks; Windows native and human acceptance remain separate')
if __name__=='__main__':main()
