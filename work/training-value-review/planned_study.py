from campaigns import *
if __name__=='__main__':
 cases=[]
 for who,formation,exposure,diff in itertools.product(CHARS,['fixed','rotate','reserve'],['main','all'],['standard','hard']):
  cases.append(dict(name=f'{who}/{formation}/{exposure}/{diff}/next-duty',training_actor=who,behavior='cautious',training_rule='current',training='favorite',training_decision='next_duty',formation=formation,activation_day=max(7,CHARS[who]['join']+5),favorites=[who]+[a for a in ['lin','xu','su'] if a!=who][:2],difficulty=diff,variant='A',ending='evacuation',choice_index=0,sides='all' if exposure=='all' else False,exposure=exposure,shop=False,pack=1,treat=True,service=True))
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:rows=list(pool.map(run,cases))
 (ROOT/'outputs/training-planned.json').write_text(json.dumps(dict(version='0.17',scenarios=rows,actual_battles=sum(len(r['battles']) for r in rows),scope='96additional paid-state campaigns; train only if a level is crossed and forecast next-day main party still includes that actor. No future battle outcome or perfect-route search. Compared to matching no-training cases.'),ensure_ascii=False,indent=2)+'\n');print('PLANNED',len(rows),flush=True)
