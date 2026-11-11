from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'game/data';F=D/'final_design';V='0.15-player-ready'
def put(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
a=json.loads((F/'abilities.json').read_text());p=D/'characters.json';chars=json.loads(p.read_text())
for c in chars:c['abilities']=[x['name'] for x in a if x['actor']==c['id'] and x.get('production_status')=='active'];c['script_profile_ref']='final_design/character_scripts.json#profiles.'+c['id']
put(p,chars)
for file in ['production_scope.json','integration.json']:
 p=F/file;x=json.loads(p.read_text());x['version']=V
 if file=='production_scope.json':x['growth']['L3']='第二专长；固定保留两项。江朔的第一专长同时扩为2格交接，见growth_identity_contract.level3_modifiers。'
 else:x['authority']='0.15当前设计由design_manifest.json索引；0.14及更早报告保留为历史证据。人物正文见character_scripts.json，经济见../campaign_economy_contract.json。正式开发仍暂停。'
 put(p,x)
for name in ['development.json','logic-audit.json']:
 p=ROOT/'game/docs'/name;x=json.loads(p.read_text());x['design_version']=V;x['player_ready_review']='../../outputs/player-ready-review.html';x['authored_scripts']='../../outputs/character-script-final.html';x['formal_development_started']=False;put(p,x)
p=ROOT/'game/README.txt';s=p.read_text().replace('设计版本：0.14（当前继续设计，暂不进入正式开发），2026-11-02','设计版本：0.15（当前继续设计，暂不进入正式开发），2026-11-03')
if '0.15当前修订' not in s:s+='\n0.15当前修订：../outputs/player-ready-review.html\n人物完整剧本：../outputs/character-script-final.html\n当前设计复核：python3 work/player-ready-review/rebuild.py（在工作区根目录；只处理设计与离线模型）\n0.14及更早报告属于历史；当前经济、角色修订与人物全文以0.15为准。\n'
p.write_text(s)
p=ROOT/'work/final-design/build_report.py';s=p.read_text().replace("('0.12','0.13','0.14')","('0.12','0.13','0.14','0.15')").replace("('0.13','0.14')","('0.13','0.14','0.15')").replace("SCOPE['version'].startswith('0.14')","SCOPE['version'].startswith(('0.14','0.15'))")
s=s.replace('初始60资金/8物资/2零件；主任务成功24/2/2、部分14/1/1、失败6/0/0；支线16/1/1、8/0/0、0/0/0。','初始30资金/6物资/2零件；主任务成功10/1/1、部分7/0/0、失败6/0/0；支线6/0/0、3/0/0、0/0/0。明确交接目标另按0.15经济表奖励；旧的任意额外目标统一物资奖励已撤销。')
p.write_text(s)
p=F/'growth_identity_contract.json';x=json.loads(p.read_text());x['date']='2026-11-03';put(p,x)
print('Synced current authority and character abilities')
