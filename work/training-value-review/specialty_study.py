from campaigns import *
if __name__=='__main__':
 cases=[]
 for who,rule,exposure,diff in itertools.product(CHARS,['none','current'],['main','all'],['standard','hard']):
  cases.append(dict(name=f'{who}/{rule}/{exposure}/{diff}/specialty',training_actor=who,behavior='cautious',training_rule=rule,training='none' if rule=='none' else 'favorite',formation='fixed',activation_day=max(7,CHARS[who]['join']+5),favorites=[who]+[a for a in ['lin','xu','su'] if a!=who][:2],difficulty=diff,variant='A',ending='evacuation',choice_index=0,sides='all' if exposure=='all' else False,exposure=exposure,shop=False,pack=1,treat=True,service=True,specialty_intent=True))
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:rows=list(pool.map(run,cases))
 (ROOT/'outputs/training-specialty.json').write_text(json.dumps(dict(version='0.17',scenarios=rows,actual_battles=sum(len(r['battles']) for r in rows),scope='64paired campaigns with prespecified profession intent; same intent in untrained/trained, no best-result selection.'),ensure_ascii=False,indent=2)+'\n');print('SPECIALTY',len(rows),flush=True)
