"""Full maps and exact geometric alternatives, not human playtest observations."""
from pathlib import Path
import json
from choices import ChoiceBattle,SPEC,CONTRACT,distance,adjacent
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs'
p=ROOT/'work/approach-review/protocol_witnesses.py'
src=p.read_text().split('out=[]')[0].replace('from encounter_choices import ChoiceBattle,distance,adjacent','from choices import ChoiceBattle,distance,adjacent').replace("e=self.e[self.spec['source_enemy']];control=self.spec['linked_controls'][0]","e=self.e[self.asset_spec['source_enemy']];control=self.asset_spec['linked_controls'][0]")
ns={'__file__':str(p),'__name__':'player_choice_witness_adapter'};exec(compile(src,str(p),'exec'),ns)
B=ns['B'];P=ns['P'];records=[]
for name,g in [('relay',ns['RelayWitness']()),('ordinary_handoff',ns['RelayWitness'](False)),('pull_without_added_wait',ns['PullWitness']())]:
 r=g.run();r.pop('used',None);r.update(witness_name=name,scope='Normal spawn and actual AP/paths, controlled level2 and an already learned pair bundle; earned campaign training is separately checked.');records.append(r)
 print(name,r['success'],r['rounds'],r['secured'],flush=True)
for mid in ['M10','M21','S11']:
 for mode in ['independent','protected']:
  g=ChoiceBattle(B[mid],[x[0] for x in B[mid]['mandatory_groups']],P,{a:3 for a in P},approach=mode,watchers=[0,2] if len(SPEC['services'][mid]['posts'])==2 else [0],skills=True,trained=[('lin','su',k) for k in CONTRACT['cooperation_training']['unlocks']],style='controls')
  r=g.run();r.pop('used',None);r.update(witness_name=mid+'_'+mode,scope='Same starting party/level/target set and operator assignment; only cooperation policy differs.');records.append(r)
g=ChoiceBattle(B['M22'],['handover'],P,{a:3 for a in P},skills=False,ambition=True,style='controls');r=g.run();r.pop('used',None);r['witness_name']='M22_ordinary_no_added_wait';records.append(r)
(O/'player-choice-witnesses.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
