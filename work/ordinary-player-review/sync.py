from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];F=ROOT/'game/data/final_design'
p=F/'ordinary_player_contract.json';d=json.loads(p.read_text());d['authority']='以design_manifest的当前领域文件为准；本轮未明确修订的0.15规则继续有效。108条普通整局未发现经济阻断，维持0.15基础收入，不继续削减。'
d['resolved']=list(dict.fromkeys(d['resolved']+['stale specialty hint expires','retired item command rejection','level5 He barrier5HP and Ye straight range2','training recommendation requires visible use and deployability']))
d['review_status']='Design/offline review complete for enumerated scope; human usability and artistic quality not validated.'
d['coverage_counts']=dict(structural_trials=4248,roster_trials=11456,legal_trio_goal_contexts=1432,earned_campaigns=108,growth_campaigns=30,service_contexts=384,personal_dialogue_states=2352)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'work/final-design/build_report.py';s=p.read_text().replace("'0.14','0.15'","'0.14','0.15','0.16'");p.write_text(s)
for name in ['routes.py','campaigns.py']:
 p=ROOT/'work/ordinary-player-review'/name;s=p.read_text().replace("default='ordinary-player-before-","default='ordinary-player-after-");p.write_text(s)
print('Syncedcurrentauthority andsafe rerun defaults')
