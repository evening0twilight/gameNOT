"""Package the P4 acceptance candidate, protecting all prior delivery evidence."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,re,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/windows-p4'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
receipt_path=OUT/'build-receipt.json'
receipt=json.loads(receipt_path.read_text())
sources=sorted(p for folder in ['scripts','scenes','data','assets'] for p in (ROOT/'game'/folder).rglob('*') if p.is_file() and p.suffix not in ['.import','.uid'])+[ROOT/'game/project.godot',ROOT/'game/export_presets.cfg']
if any(p.stat().st_mtime>receipt_path.stat().st_mtime for p in sources):raise SystemExit('Source newer than final build; rebuild required')
for name,value in receipt['sha256'].items():
 if digest(OUT/name)!=value:raise SystemExit('Export hash mismatch: '+name)
log=(ROOT/'outputs/p4-build.log').read_text()
for marker in ['WINDOWS_EXPORT_OK:','CHECK_OK:','P4_PRODUCT_RESULTS:','P4_HISTORY_RESULTS:','P4_PRESENTATION_RESULTS:']:
 if marker not in log:raise SystemExit('Missing final build marker: '+marker)
if 'SCRIPT ERROR:' in log or '\nERROR:' in log or re.search(r'failures=[1-9]|[1-9][0-9]* failed',log):raise SystemExit('Build has failures')
preserved=json.loads((ROOT/'docs/p4-preserved-files.json').read_text())
for name,value in preserved.items():
 if digest(ROOT/name)!=value:raise SystemExit('Historical evidence changed: '+name)
matrices=[entry for difficulty in ['relaxed','standard','hard'] for entry in json.loads((ROOT/f'outputs/p4-matrix-{difficulty}.json').read_text())]
assert len(matrices)==216 and all(r['can_continue'] and r['outcome']=='success' and r['specialties_used'] is False and r['equipment_used'] is False for r in matrices)
profiles=[json.loads((ROOT/f'outputs/p4-profile-{name}.json').read_text()) for name in ['no_training','few_sides','fixed_favorites','injury_rotation']]
assert all(p['finished'] and len(p['days'])==24 for p in profiles)
campaigns=json.loads((ROOT/'outputs/p4-campaign-paths.json').read_text())
assert len(campaigns)==4 and all(c['finished'] and len(c['days'])==24 for c in campaigns)
gui=json.loads((ROOT/'outputs/p4-gui/replay.json').read_text())
assert len(gui['records'])==36 and all(r['ok'] and r['screen']!=r['primary'] for r in gui['records'])
for name in ['outputs/p4-gui-replay.log','outputs/p4-visual-review.log']:
 text=(ROOT/name).read_text()
 if 'SCRIPT ERROR:' in text or '\nERROR:' in text:raise SystemExit('GUI error: '+name)
audio=json.loads((ROOT/'docs/p4-audio-assets.json').read_text())
for asset in audio['assets']:assert digest(ROOT/asset['path'])==asset['sha256']
evidence=['outputs/p4-build.log','outputs/p4-path-exploration.json','outputs/p4-campaign-paths.json','outputs/p4-gui/replay.json','outputs/p4-visual-review/record.json','docs/p4-preserved-files.json','docs/p3-user-feedback.json','docs/p4-audio-assets.json']+[f'outputs/p4-matrix-{d}.json' for d in ['relaxed','standard','hard']]+[f'outputs/p4-profile-{p["profile"]}.json' for p in profiles]
receipt.update({'runtime_revision':5,'source_sha256':{str(p.relative_to(ROOT)):digest(p) for p in sources},'test_source_sha256':{str(p.relative_to(ROOT)):digest(p) for p in sorted((ROOT/'game/tests').glob('*.gd'))},'evidence_sha256':{name:digest(ROOT/name) for name in evidence}})
receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
for source,target in [('game/assets/fonts/OFL.txt','OFL.txt'),('docs/p4-validation.txt','validation.txt'),('docs/p4-windows-checklist.txt','windows-checklist.txt'),('docs/p4-audio-assets.json','audio-assets.json'),('docs/p3-visual-assets.json','visual-assets.json'),('docs/p3-visual-prompts.json','visual-prompts.json')]:shutil.copyfile(ROOT/source,OUT/target)
(OUT/'README.txt').write_text('''夜潮事务所 — P4 产品验收候选版
解压后保持night-tide.exe和night-tide.pck同目录，双击exe。
已有P3存档可复制迁移；P4保存到独立saves/p4，原P3文件不覆写。
在设置中可新建独立周目体验M01新提示；旧周目保留，可切换。

先看地图上方目标，选择队员、行动、目标。底部先预览，再次点同一目标或确认执行。
右键/Esc取消选择；空格预览结束回合；F1查看帮助。目标达成后仍需交付/离场。
救援：稳定→拾起→移动到箭头出口→交付。施工需满足前置；任务页可精确选对象。
每晚两项项目与两段短谈分别计数，不要求每天用满。零资源仍可继续主线。
装备/设施、记录核查与历史补救在营地；专长、装备不是主线必须钥匙。
严峻模式未救出的失能队员永久医疗离队，出发前会披露并要求理解确认。
完成一周目后，新建存档可选择天气B；没有资源/经验继承。
声音设置中音乐/音效可独立调整或全静音；设置也可导出本机运行记录。

Windows原生、参考设备性能、DPI与真人试玩仍需按windows-checklist.txt实测。
本包不是发行版本，不以自动路径成功替代理解、趣味性与审美判断。
''',encoding='utf-8')
names=['night-tide.exe','night-tide.pck','build-receipt.json','README.txt','OFL.txt','validation.txt','windows-checklist.txt','audio-assets.json','visual-assets.json','visual-prompts.json']
package=ROOT/'build/night-tide-windows-p4.zip'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
 for name in names:z.write(OUT/name,name)
with zipfile.ZipFile(package) as z:
 assert z.testzip() is None
 for name,value in receipt['sha256'].items():assert hashlib.sha256(z.read(name)).hexdigest()==value
report={'date':datetime.now(ZoneInfo('Asia/Singapore')).date().isoformat(),'scope':'P4 product acceptance candidate; no release approval','p3_user_acceptance':json.loads((ROOT/'docs/p3-user-feedback.json').read_text()),'test_markers':re.findall(r'^.*(?:RESULTS:|RULE CHECKS|CHECK_OK:|WINDOWS_EXPORT_OK:).*$',log,re.M),'matrix':{'paths':len(matrices),'success':sum(r['outcome']=='success' for r in matrices),'injury_free':sum(not r['injured'] for r in matrices),'specialties_or_equipment_used':False},'continuous_campaigns':[{'mode':c['mode'],'days':len(c['days']),'ending':c['ending']} for c in campaigns],'profiles':[{'profile':p['profile'],'days':len(p['days']),'ending':p['ending']} for p in profiles],'gui_host':gui,'historical_hashes_verified':len(preserved),'windows_native':'pending_P4_user_test','reference_hardware_metrics':'pending_individual_measurements','H01_H04':'pending_real_player_evidence','final_art_audio_editorial':'pending_human_review','release_ready':False,'build':receipt,'package':str(package.relative_to(ROOT)),'package_bytes':package.stat().st_size,'package_sha256':digest(package)}
(ROOT/'docs/p4-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('P4_PACKAGE_OK:',package,report['package_sha256'],report['package_bytes'])
