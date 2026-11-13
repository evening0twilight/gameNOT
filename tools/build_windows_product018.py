"""Export the same 0.18 game; never overwrite previous release evidence."""
import re
import argparse,hashlib,json,os,struct,subprocess,tempfile,shutil,zipfile,sys
from pathlib import Path
from check_product018 import ROOT,ENGINE,digest,history_status,source_hashes,run
from bootstrap import templates_dir

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--allow-missing-history',action='store_true');parser.add_argument('--candidate',default='product018');parser.add_argument('--review-dir',default='docs/p4-018-20261112');args=parser.parse_args()
    assert re.fullmatch(r'[a-z0-9][a-z0-9-]*',args.candidate),'Invalid candidate label'
    review=(ROOT/args.review_dir).resolve()
    assert review.is_relative_to((ROOT/'docs').resolve()),'Review directory must be under docs/'
    review_name=str(review.relative_to(ROOT))
    checks=json.loads((ROOT/f'outputs/{args.candidate}-checks.json').read_text())
    assert checks['full'],'Run python3 tools/check_product018.py --full first'
    assert checks['source_hashes']==source_hashes(),'Game sources changed after the final check'
    history=history_status(args.allow_missing_history)
    engine=os.environ.get('GODOT',str(ENGINE))
    assert (templates_dir()/'windows_release_x86_64.exe').is_file(),'Missing locked export template'
    out=ROOT/f'build/windows-{args.candidate}';out.mkdir(parents=True,exist_ok=True)
    run([engine,'--headless','--path','game','--export-release','Windows Desktop',str(out/'night-tide.exe')],'windows-export',prefix=args.candidate)
    with (out/'night-tide.exe').open('rb') as f:
        assert f.read(2)==b'MZ';f.seek(0x3c);offset=struct.unpack('<I',f.read(4))[0];f.seek(offset)
        assert f.read(4)==b'PE\0\0' and struct.unpack('<H',f.read(2))[0]==0x8664
    with tempfile.TemporaryDirectory(prefix='night-tide-product018-') as empty:
        run([engine,'--headless','--path',empty,'--main-pack',str(out/'night-tide.pck'),'--quit-after','3'],'exported-pack',prefix=args.candidate)
    receipt={'candidate':args.candidate,'design':'0.18','runtime_revision':8,'pe_architecture':'x86_64','windows_native_tested':False,'human_acceptance':False,'exported_pack_boot_on_macos':sys.platform=='darwin','exported_pack_boot_host':sys.platform,'history':history,'sha256':{p.name:digest(p) for p in out.iterdir() if p.suffix in ['.exe','.pck']},'source_hashes':checks['source_hashes']}
    (out/'build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    copies={'game/assets/fonts/OFL.txt':'OFL.txt','docs/baseline018-engine-license.txt':'Godot-LICENSE.txt','docs/asset-register.csv':'asset-sources.csv','docs/product018-player-guide.txt':'README.txt','docs/product018-alignment.txt':'design-alignment.txt','docs/baseline018-windows-checklist.txt':'Windows-checklist.txt','docs/product018-validation.txt':'validation.txt','tools/windows_acceptance_baseline018.cmd':'Run-Windows-Checks.cmd','docs/product018-image-prompts.json':'image-generation-prompts.json','docs/product018-audio.json':'audio-production.json','docs/product018-icons.json':'icon-production.json'}
    review_images={}
    if args.candidate!='product018':
        copies.pop('docs/product018-validation.txt')
        copies.pop('docs/product018-alignment.txt')
        copies.update({f'{review_name}/validation.md':'validation.txt','docs/p4-018-remaining.md':'CURRENT-STATUS.md',f'{review_name}/windows-review.md':'THIS-BUILD-REVIEW.md',f'{review_name}/playtest-form.csv':'playtest-form.csv'})
        if (review/'review.md').is_file():
            copies[f'{review_name}/review.md']='PRODUCT-REVIEW.md'
            for source in re.findall(r'\]\(\.\./\.\./(outputs/[a-zA-Z0-9_-]+\.png)\)',(review/'review.md').read_text()):
                assert (ROOT/source).is_file(),'Missing review image: '+source
                review_images[source]='review-images/'+Path(source).name
            copies.update(review_images)
        if (review/'image-prompts.json').is_file():copies[f'{review_name}/image-prompts.json']='current-image-generation-prompts.json'
        for audio_doc in ['audio-generated.json','audio-inventory.json','audio-handoff.md','audio-model-review.json']:
            if (review/audio_doc).is_file():copies[f'{review_name}/{audio_doc}']=audio_doc
    for source,target in copies.items():
        (out/target).parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/source,out/target)
    if review_images:
        report=out/'PRODUCT-REVIEW.md'
        body=report.read_text()
        for source,target in review_images.items():body=body.replace('](../../'+source+')',']('+target+')')
        report.write_text(body)
    if args.candidate!='product018':
        readme=out/'README.txt'
        readme.write_text('候选版本：'+args.candidate+'。这是开发候选，P4最终验收尚未通过；本包素材与功能范围以随包记录为准。先读THIS-BUILD-REVIEW.md、CURRENT-STATUS.md和build-receipt.json。\n\n'+readme.read_text())
    archive=ROOT/('build/night-tide-0.18-windows.zip' if args.candidate=='product018' else f'build/night-tide-0.18-{args.candidate}-windows.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for name in ['night-tide.exe','night-tide.pck','build-receipt.json']+list(copies.values()):z.write(out/name,name)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name in ['night-tide.exe','night-tide.pck']:assert hashlib.sha256(z.read(name)).hexdigest()==receipt['sha256'][name]
    history=history_status(args.allow_missing_history)
    record={'package':str(archive.relative_to(ROOT)),'bytes':archive.stat().st_size,'sha256':digest(archive),'build':receipt,'windows_native_tested':False,'human_acceptance':False,'preserved_files':history['verified'],'history':history}
    (ROOT/f'docs/{args.candidate}-build.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print('PRODUCT018_WINDOWS_PACKAGE_OK:',archive,record['sha256'])
if __name__=='__main__':main()
