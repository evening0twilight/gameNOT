"""Package the validated P2 build without altering P1 release evidence."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import zipfile
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'build/windows'
receipt_path=out/'build-receipt.json'
receipt=json.loads(receipt_path.read_text())
sources=sorted(p for folder in ['scripts','scenes','data','assets'] for p in (ROOT/'game'/folder).rglob('*') if p.is_file() and p.suffix not in ['.import','.uid'])+[ROOT/'game/project.godot',ROOT/'game/export_presets.cfg']
if any(p.stat().st_mtime>receipt_path.stat().st_mtime for p in sources):raise SystemExit('Source newer than build receipt; rebuild required')
for name,digest in receipt['sha256'].items():
    if hashlib.sha256((out/name).read_bytes()).hexdigest()!=digest:raise SystemExit('Build hash mismatch: '+name)
log=(ROOT/'outputs/p2-build.log').read_text()
if 'WINDOWS_EXPORT_OK:' not in log or 'SCRIPT ERROR:' in log or '\nERROR:' in log:raise SystemExit('Clean complete P2 build log required')
receipt['runtime_revision']=3
receipt['source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
for source,target in [('game/assets/fonts/OFL.txt','OFL.txt'),('docs/p2-validation.txt','validation.txt'),('docs/p2-windows-checklist.txt','windows-checklist.txt'),('docs/p2-visual-assets.json','visual-assets.json'),('docs/p2-visual-prompt-set.json','visual-prompts.json')]:shutil.copyfile(ROOT/source,out/target)
(out/'README.txt').write_text('''夜潮事务所 — P2 第一章候选版
解压后保持 night-tide.exe 与 night-tide.pck 同目录，双击 exe。
内容：M01–M06、S01–S03；第一章结束后停在章末，不进入后续章节。
从结算页选择当日可用支线，再进营地；营地准备出发可选择三人。
第4日陈砚加入。主线缺员可用临时支援；支线必须三名可用正式成员。
包含阶段训练、带教、人物故事、关系约定、生活片段、社区回访及章末事实记录。
顶部设置可选中文、伪本地化测试和字号，保存/读取手动槽。
P2存档位于 Godot app_userdata/夜潮事务所/saves/p2/；首次可复制兼容P1存档，原P1槽保留。
每个有效行动自动保存；动作预览可以取消，战术撤销不可越过结束回合与结算。
半写实人物、六地点背景、设备与机器素材已集成。战斗仍为二维格点战术界面。
本包为P2候选构建；P1 Windows通过报告不等于本包已经在Windows实机验证。
请看 validation.txt 和 windows-checklist.txt。字体许可见 OFL.txt。
''',encoding='utf-8')
package=ROOT/'build/night-tide-windows-p2.zip'
names=['night-tide.exe','night-tide.pck','build-receipt.json','README.txt','OFL.txt','validation.txt','windows-checklist.txt','visual-assets.json','visual-prompts.json']
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
    for name in names:z.write(out/name,name)
with zipfile.ZipFile(package) as z:
    for name,digest in receipt['sha256'].items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
report={'date':'2026-11-05','scope':'P2 first chapter candidate','test_markers':re.findall(r'^.*(?:RESULTS:|RULE CHECKS|CHECK_OK:|WINDOWS_EXPORT_OK:).*$',log,re.M),'windows_native':'pending_user_validation_of_P2','p1_windows':'passed_user_report; retained separately','human_visual_acceptance':'pending; not inferred from automated tests','build':receipt,'package':str(package.relative_to(ROOT)),'package_sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'package_bytes':package.stat().st_size}
(ROOT/'docs/p2-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('P2_PACKAGE_OK:',package,report['package_sha256'])
