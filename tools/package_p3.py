"""Package the validated P3 build without altering P1 release evidence."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import zipfile
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'build/windows-p3'
receipt_path=out/'build-receipt.json'
receipt=json.loads(receipt_path.read_text())
sources=sorted(p for folder in ['scripts','scenes','data','assets'] for p in (ROOT/'game'/folder).rglob('*') if p.is_file() and p.suffix not in ['.import','.uid'])+[ROOT/'game/project.godot',ROOT/'game/export_presets.cfg']
if any(p.stat().st_mtime>receipt_path.stat().st_mtime for p in sources):raise SystemExit('Source newer than build receipt; rebuild required')
for name,digest in receipt['sha256'].items():
    if hashlib.sha256((out/name).read_bytes()).hexdigest()!=digest:raise SystemExit('Build hash mismatch: '+name)
log=(ROOT/'outputs/p3-build.log').read_text()
if 'WINDOWS_EXPORT_OK:' not in log or 'SCRIPT ERROR:' in log or '\nERROR:' in log:raise SystemExit('Clean complete P3 build log required')
preserved=json.loads((ROOT/'docs/p3-preserved-files.json').read_text())
for name,digest in preserved.items():
    if not (ROOT/name).is_file() or hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise SystemExit('Historical evidence changed: '+name)
gui=json.loads((ROOT/'outputs/p3-gui/replay.json').read_text())
if len(gui['records'])!=36 or not all(r['ok'] and r['screen']!=r['primary'] for r in gui['records']):raise SystemExit('36 non-primary-display GUI paths required')
campaigns=json.loads((ROOT/'outputs/p3-campaign-paths.json').read_text())
if len(campaigns)!=4 or not all(len(c['days'])==24 and c['finished'] for c in campaigns):raise SystemExit('Four complete 24-day records required')
receipt['runtime_revision']=4
receipt['test_source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'game/tests').glob('*.gd'))}
receipt['evidence_sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['outputs/p3-build.log','outputs/p3-path-exploration.json','outputs/p3-campaign-paths.json','outputs/p3-gui/replay.json','docs/p3-preserved-files.json']}
receipt['source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
for source,target in [('game/assets/fonts/OFL.txt','OFL.txt'),('docs/p3-validation.txt','validation.txt'),('docs/p3-windows-checklist.txt','windows-checklist.txt'),('docs/p3-visual-assets.json','visual-assets.json'),('docs/p3-visual-prompts.json','visual-prompts.json')]:shutil.copyfile(ROOT/source,out/target)
(out/'README.txt').write_text("""夜潮事务所 — P3 四章候选版
解压后保持 night-tide.exe 与 night-tide.pck 同目录，双击exe。
24主线/12支线、八位队员、人物/关系/生活/社区与章末共96场景、三世界结局。
每晚仅2段人物短谈，未读可以保留；不是同一周目必看96场。
地图上方显示必需目标；可点“查看现场”。先选行动再点棋盘，目标页可按对象选择。
救援需稳定→拾起→走到出口→交付；通用交互可处理装置，持续目标需结束回合推进。
结算后可选择当日支线或进入营地；营地可配队、训练、处理故事和安排后勤。
第23日晚核查未解决事项、选择终局路线；第24日结算后不可返营。
P3使用独立saves/p3槽，首次可复制读取兼容P2自动档；原P2文件保留。
设置中可手动存读、恢复备份、调整字号和语言；en_XA仅伪本地化测试。
结局后可只读查看本周目记录，也可新建独立周目；旧周目与手动槽保留，可在设置切换。
Windows原生、DPI、性能、真人理解/趣味性/美术验收待验证。请阅读validation.txt和windows-checklist.txt。
""",encoding='utf-8')
package=ROOT/'build/night-tide-windows-p3.zip'
names=['night-tide.exe','night-tide.pck','build-receipt.json','README.txt','OFL.txt','validation.txt','windows-checklist.txt','visual-assets.json','visual-prompts.json']
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
    for name in names:z.write(out/name,name)
with zipfile.ZipFile(package) as z:
    for name,digest in receipt['sha256'].items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
report={'date':datetime.now(ZoneInfo('Asia/Singapore')).date().isoformat(),'scope':'P3 four-chapter content candidate','test_markers':re.findall(r'^.*(?:RESULTS:|RULE CHECKS|CHECK_OK:|WINDOWS_EXPORT_OK:).*$',log,re.M),'windows_native':'pending_user_validation_of_P3','p1_windows':'passed_user_report; retained separately','human_visual_acceptance':'pending; not inferred from automated tests','p2_user_feedback':json.loads((ROOT/'docs/p2-user-feedback.json').read_text()),'gui_host':gui,'campaigns':[{'mode':c['mode'],'days':len(c['days']),'ending':c['ending']} for c in campaigns],'historical_hashes_verified':len(preserved),'full_product_acceptance':False,'build':receipt,'package':str(package.relative_to(ROOT)),'package_sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'package_bytes':package.stat().st_size}
(ROOT/'docs/p3-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('P3_PACKAGE_OK:',package,report['package_sha256'])
