from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
s=(ROOT/'work/full-audit/verify.py').read_text().split('for key in SCOPE')[0];exec(compile(s,str(ROOT/'work/full-audit/verify.py'),'exec'))
from social import qualified
rows=[]
g=RelationshipLedger('choice');g.day=2;g.phase='camp';g.scene('P_lin_1','share');r=next(x for x in g.records if x['kind']=='story_choice');rows.append(dict(id='first_choice_ignored',requested='share',stored=r['choice'],reproduced=r['choice']!='share'))
g=RelationshipLedger('mo');g.day=18;g.phase='camp'
for a in g.crew:g.crew[a]['joined']=True
g.read_nodes.add('P_mo_1');g.scene('P_mo_2','redact');rows.append(dict(id='promise_creates_release',reproduced=any(r['kind']=='public_record_release' for r in g.records),records=g.records))
g=fixture('xu',5);g.h[1]['p']=(3,5);g.rows[4][3]='X';g.h[0]['carry']='r1';g.objects['r1'].update(carrier=0,stable=True);g.use(0,'xu_1',destination=(4,4));rows.append(dict(id='rope_transport_missing',reproduced=not any(r['action']=='transport_path' for r in g.log),log=g.log))
# Use the exact failed ordinary campaign situation, not a newly optimized plan.
import sys;sys.path.insert(0,str(ROOT/'work/ordinary-player-review'));from policies import battle
p=['he','ye','chen'];g=battle(B['M12'],['backup','drive'],p,{'he':2,'ye':3,'chen':3},'mixed',['e'],gear={'medkit':0,'crowbar':0,'scanner':1,'med_dose':2},difficulty='standard',variant='A',delay=1);r=g.run();rows.append(dict(id='lost_prerequisite_stall',reproduced=g.objects['backup']['lost'] and not g.objects['drive']['lost'] and r['rounds']==15,rounds=r['rounds'],healthy_extracted=r['healthy_extracted'],downed=r['downed'],last_action_round=max(z['round'] for z in r['log'] if z['action'] not in ['intents','round_end','water_added','object_lost'])))
assert all(r['reproduced'] for r in rows)
(ROOT/'outputs/ordinary-player-before-bugs.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print('REPRODUCED',len(rows))
