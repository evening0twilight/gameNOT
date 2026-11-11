"""Export the same 0.18 game; never overwrite previous release evidence."""
import hashlib,json,os,struct,subprocess,tempfile,shutil,zipfile
from pathlib import Path
from check_baseline018 import ROOT,ENGINE,digest,preserved,source_hashes,run
from bootstrap import templates_dir

def main():
    checks=json.loads((ROOT/'outputs/baseline018-checks.json').read_text())
    assert checks['full'],'Run python3 tools/check_baseline018.py --full first'
    assert checks['source_hashes']==source_hashes(),'Game sources changed after the final check'
    preserved()
    engine=os.environ.get('GODOT',str(ENGINE))
    assert (templates_dir()/'windows_release_x86_64.exe').is_file(),'Missing locked export template'
    out=ROOT/'build/windows-baseline018';out.mkdir(parents=True,exist_ok=True)
    run([engine,'--headless','--path','game','--export-release','Windows Desktop',str(out/'night-tide.exe')],'windows-export')
    with (out/'night-tide.exe').open('rb') as f:
        assert f.read(2)==b'MZ';f.seek(0x3c);offset=struct.unpack('<I',f.read(4))[0];f.seek(offset)
        assert f.read(4)==b'PE\0\0' and struct.unpack('<H',f.read(2))[0]==0x8664
    with tempfile.TemporaryDirectory(prefix='night-tide-baseline018-') as empty:
        run([engine,'--headless','--path',empty,'--main-pack',str(out/'night-tide.pck'),'--quit-after','3'],'exported-pack')
    receipt={'design':'0.18','runtime_revision':7,'pe_architecture':'x86_64','windows_native_tested':False,'exported_pack_boot_on_macos':True,'sha256':{p.name:digest(p) for p in out.iterdir() if p.suffix in ['.exe','.pck']},'source_hashes':checks['source_hashes']}
    (out/'build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    copies={'game/assets/fonts/OFL.txt':'OFL.txt','docs/baseline018-engine-license.txt':'Godot-LICENSE.txt','docs/asset-register.csv':'asset-sources.csv','docs/baseline018-player-guide.txt':'README.txt','docs/baseline018-alignment.txt':'design-alignment.txt','docs/baseline018-windows-checklist.txt':'Windows-checklist.txt','docs/baseline018-validation.txt':'validation.txt','tools/windows_acceptance_baseline018.cmd':'Run-Windows-Checks.cmd'}
    for source,target in copies.items():shutil.copy2(ROOT/source,out/target)
    archive=ROOT/'build/night-tide-windows-baseline018.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for name in ['night-tide.exe','night-tide.pck','build-receipt.json']+list(copies.values()):z.write(out/name,name)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name in ['night-tide.exe','night-tide.pck']:assert hashlib.sha256(z.read(name)).hexdigest()==receipt['sha256'][name]
    record={'package':str(archive.relative_to(ROOT)),'bytes':archive.stat().st_size,'sha256':digest(archive),'build':receipt,'windows_native_tested':False,'human_acceptance':False,'preserved_files':preserved()}
    (ROOT/'docs/baseline018-build.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print('BASELINE018_WINDOWS_PACKAGE_OK:',archive,record['sha256'])
if __name__=='__main__':main()
