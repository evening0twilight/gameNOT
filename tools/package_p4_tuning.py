"""Package the feedback revision without overwriting prior P4 delivery artifacts."""
from pathlib import Path
import hashlib,json,re,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/windows-p4-tuning'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receipt_path=OUT/'build-receipt.json'
receipt=json.loads(receipt_path.read_text())
sources=sorted(p for folder in ['scripts','scenes','data','assets'] for p in (ROOT/'game'/folder).rglob('*') if p.is_file() and p.suffix not in ['.import','.uid'])+[ROOT/'game/project.godot',ROOT/'game/export_presets.cfg']
assert all(p.stat().st_mtime<=receipt_path.stat().st_mtime for p in sources),'Source newer than build'
for name,value in receipt['sha256'].items():assert digest(OUT/name)==value,name
log=(ROOT/'outputs/p4-tuning-build.log').read_text()
for marker in ['WINDOWS_EXPORT_OK:','CHECK_OK:','P4_PRODUCT_RESULTS:','P4_HISTORY_RESULTS:','P4_PRESENTATION_RESULTS:','P4_FEEDBACK_RESULTS:','P4_TUNING_RESULTS:']:
 assert marker in log,marker
assert 'SCRIPT ERROR:' not in log and '\nERROR:' not in log and not re.search(r'failures=[1-9]|[1-9][0-9]* failed',log)
preserved={}
for name in ['p4-preserved-files.json','p4-feedback-preserved.json','p4-tuning-preserved.json']:preserved.update(json.loads((ROOT/'docs'/name).read_text()))
for name,value in preserved.items():assert digest(ROOT/name)==value,'Historical evidence changed: '+name
matrices=[r for d in ['relaxed','standard','hard'] for r in json.loads((ROOT/f'outputs/p4-tuning-matrix-{d}.json').read_text())]
assert len(matrices)==216 and all(r['can_continue'] and r['outcome'] in ['success','partial'] and r['specialties_used'] is False and r['equipment_used'] is False for r in matrices)
# Keep the fixed-route comparison honest: hard M05 now needs threat control.
partials=[r for r in matrices if r['outcome']=='partial']
assert {(r['mission'],r['difficulty'],r['variant']) for r in partials}=={('M05','hard','A'),('M05','hard','B')}
hard_routes=json.loads((ROOT/'outputs/p4-tuning-hard-route.json').read_text())
assert len(hard_routes)==2 and {r['variant'] for r in hard_routes}=={'A','B'} and all(r['outcome']=='success' and not r['specialties_used'] and not r['equipment_used'] for r in hard_routes)
hard_log=(ROOT/'outputs/p4-tuning-hard-route.log').read_text()
assert 'P4_HARD_ROUTE_RESULTS: paths=2 failures=0' in hard_log and 'SCRIPT ERROR:' not in hard_log and '\nERROR:' not in hard_log
campaigns=json.loads((ROOT/'outputs/p4-tuning-campaign-paths.json').read_text())
assert len(campaigns)==4 and all(c['finished'] and len(c['days'])==24 for c in campaigns)
profiles=[json.loads((ROOT/f'outputs/p4-tuning-profile-{p}.json').read_text()) for p in ['no_training','few_sides','fixed_favorites','injury_rotation']]
assert all(p['finished'] and len(p['days'])==24 for p in profiles)
gui=json.loads((ROOT/'outputs/p4-tuning-gui/replay.json').read_text())
assert len(gui['records'])==36 and all(r['ok'] and r['screen']!=r['primary'] for r in gui['records'])
host=json.loads((ROOT/'outputs/p4-tuning-native-host-report.json').read_text())
assert host['passed'] and host['rendered'] and host['screen']!=host['primary']
review=json.loads((ROOT/'outputs/p4-tuning-review/record.json').read_text())
movie=json.loads((ROOT/'outputs/p4-tuning-movie.json').read_text())
assert review['screen']!=review['primary'] and movie['screen']!=movie['primary']
assert len(movie['actions'])==10 and len(review['captures'])==9
for name in ['outputs/p4-tuning-gui-replay.log','outputs/p4-tuning-review.log','outputs/p4-tuning-movie.log']:
 text=(ROOT/name).read_text();assert 'SCRIPT ERROR:' not in text and '\nERROR:' not in text,name
for name in ['p4-motion-assets.json','p4-feedback-audio.json','p4-audio-assets.json']:
 for asset in json.loads((ROOT/'docs'/name).read_text())['assets']:assert digest(ROOT/asset['path'])==asset['sha256']
evidence=['outputs/p4-tuning-build.log','outputs/p4-tuning-gui/replay.json','outputs/p4-tuning-review/record.json','outputs/p4-tuning-movie.json','outputs/p4-tuning-runtime.mp4','docs/p4-user-feedback.json','docs/p4-motion-assets.json','docs/p4-motion-prompts.json','docs/p4-feedback-audio.json','outputs/p4-tuning-probe-before.json','outputs/p4-tuning-probe-after.json','outputs/p4-tuning-guided-paths.json','outputs/p4-tuning-native-host-report.json','docs/p4-tuning-hands-on.json','docs/p4-tuning-performance.json','outputs/p4-tuning-native-host-before-optimization.json','outputs/p4-tuning-media-info.json','outputs/p4-tuning-audio-levels.log','outputs/p4-tuning-hard-route.json','outputs/p4-tuning-hard-route.log']
receipt.update({'runtime_revision':6,'source_sha256':{str(p.relative_to(ROOT)):digest(p) for p in sources},'test_source_sha256':{str(p.relative_to(ROOT)):digest(p) for p in sorted((ROOT/'game/tests').glob('*.gd'))},'evidence_sha256':{name:digest(ROOT/name) for name in evidence},'p4_product_accepted':False})
receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
copies=[('game/assets/fonts/OFL.txt','OFL.txt'),('docs/p4-tuning-validation.txt','validation.txt'),('docs/p4-tuning-windows-checklist.txt','windows-checklist.txt'),('docs/p4-tuning-balance.json','p4-tuning-balance.json'),('docs/p4-tuning-performance.json','p4-tuning-performance.json'),('outputs/p4-tuning-hard-route.json','p4-tuning-hard-route.json'),('docs/p4-feedback-audio.json','feedback-audio.json'),('tools/windows_acceptance.cmd','Run-Windows-Checks.cmd'),('docs/p4-audio-assets.json','audio-assets.json'),('docs/p4-motion-assets.json','motion-assets.json'),('docs/p4-motion-prompts.json','motion-prompts.json')]
for source,target in copies:
 if target.endswith('.cmd'):(OUT/target).write_bytes((ROOT/source).read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
 else:shutil.copyfile(ROOT/source,OUT/target)
(OUT/'README.txt').write_text('''夜潮事务所 — P4 难度与引导调校版（待体验验收）
解压后保持 night-tide.exe 和 night-tide.pck 同目录，双击 exe。
旧 P4 存档可继续；新周目会显示玩法介绍，现场「怎么玩」可随时重看。
选择队员 → 选择行动 → 点目标看预览 → 再点同一目标或底部确认执行。
救援顺序：靠近 → 稳定 → 拾起 → 搬到箭头出口 → 交付。
地图下方持续提示下一步；移动时金框是这一手可达的落脚点，青绿格可移动，橙色是机器预告。

动作期间会播放步态、交互、受击等动画，并在动作时点播放声音。
空格/Esc或「跳过动画」只跳过表现，不会多走一轮或重复扣行动点。
平时空格预览结束回合，Esc/右键取消选择，F1查看帮助。
声音设置可独立调整音乐与音效，或全静音。
出勤前可选放松/标准/严峻；本次任务开始后锁定，下次出勤可改。
放松模式额外给予居民稳定/限时成果 2 回合，机器伤害减少 1；严峻机器伤害增加 1。
严峻模式未救出的失能队员会永久医疗离队，请阅读难度卡。
进行中的旧存档沿用旧伤害与期限；下次出勤采用新版。
双击 Run-Windows-Checks.cmd 可运行隔离存档自动实测，完成后打开本机报告目录。

此版针对用户反馈继续返工；不表示 P4 产品验收完成。
具体实现、自动检查与实际体验边界见 validation.txt。
''',encoding='utf-8')
package=ROOT/'build/night-tide-windows-p4-tuning.zip'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as archive:
 for name in ['night-tide.exe','night-tide.pck','build-receipt.json','README.txt']+[target for _,target in copies]:archive.write(OUT/name,name)
with zipfile.ZipFile(package) as archive:
 assert archive.testzip() is None
 for name,value in receipt['sha256'].items():assert hashlib.sha256(archive.read(name)).hexdigest()==value
report={'date':'2026-11-06','status':'P4 difficulty and guidance tuning; native host checks completed; user will test Windows later','p4_accepted':False,'release_ready':False,'tuning_checks':'outputs/p4-tuning-guided-paths.json','balance_comparison':'docs/p4-tuning-balance.json','native_host_report':json.loads((ROOT/'outputs/p4-tuning-native-host-report.json').read_text()),'test_markers':re.findall(r'^.*(?:RESULTS:|RULE CHECKS|CHECK_OK:|WINDOWS_EXPORT_OK:).*$',log,re.M),'matrix':{'paths':len(matrices),'success':sum(r['outcome']=='success' for r in matrices),'partial':len(partials),'partial_cases':[{k:r[k] for k in ['mission','difficulty','variant']} for r in partials],'alternate_hard_routes_success':len(hard_routes),'injury_free':sum(not r['injured'] for r in matrices)},'campaigns':[{'mode':c['mode'],'days':len(c['days']),'ending':c['ending']} for c in campaigns],'profiles':[{'profile':p['profile'],'days':len(p['days'])} for p in profiles],'gui_paths':len(gui['records']),'review':review,'movie':movie,'preserved_hashes_verified':len(preserved),'windows_native_tested':False,'human_motion_audio_acceptance':False,'difficulty_balance_changed':True,'build':receipt,'package':str(package.relative_to(ROOT)),'package_sha256':digest(package),'package_bytes':package.stat().st_size}
(ROOT/'docs/p4-tuning-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('P4_TUNING_PACKAGE_OK:',package,report['package_sha256'],report['package_bytes'])
