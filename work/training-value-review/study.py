from campaigns import *
import argparse

def specs(screen=False):
 for who,formation,exposure,rule,difficulty,variant in itertools.product(CHARS,['fixed','rotate','reserve'],['main'] if screen else ['main','all'],['none','legacy','stage6','stage8','stage12'] if screen else ['none','legacy','current'],['standard'] if screen else ['standard','hard'],['A'] if screen else ['A','B']):
  favorites=[who]+[a for a in ['lin','xu','su'] if a!=who][:2]
  yield dict(name='/'.join([who,formation,exposure,rule,difficulty,variant]),training_actor=who,behavior='cautious',training_rule=rule,training='none' if rule=='none' else 'favorite',formation=formation,activation_day=max(7,CHARS[who]['join']+5),favorites=favorites,difficulty=difficulty,variant=variant,ending='evacuation',choice_index=0,sides='all' if exposure=='all' else False,exposure=exposure,shop=False,pack=1,treat=True,service=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--screen',action='store_true');a=ap.parse_args();inputs=list(specs(a.screen));print('CASES',len(inputs),flush=True)
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:
  rows=[]
  for i,r in enumerate(pool.map(run,inputs),1):
   rows.append(r)
   if i%24==0:print('campaigns',i,flush=True)
 path=ROOT/'outputs'/('training-screen.json' if a.screen else 'training-campaigns.json');path.write_text(json.dumps(dict(version='0.17-candidate',scenarios=rows,actual_battles=sum(len(r['battles']) for r in rows),scope='Prespecified ordinary policies; actual earned XP/fatigue/resources. No outcome selection. Rule candidates deliberately compared; no formal game edits.'),ensure_ascii=False,indent=2)+'\n');print('DONE',path,len(rows),flush=True)
