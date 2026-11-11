from campaigns import *
if __name__=='__main__':
 cases=[]
 for who,formation in itertools.product(CHARS,['fixed','rotate','reserve']):
  cases.append(dict(name=f'{who}/{formation}/mentored',training_actor=who,behavior='cautious',training_rule='current',training='favorite',formation=formation,activation_day=max(7,CHARS[who]['join']+5),favorites=[who]+[a for a in ['lin','xu','su'] if a!=who][:2],difficulty='standard',variant='A',ending='evacuation',choice_index=0,sides='all',exposure='all',shop=False,pack=1,treat=True,service=True,prefer_mentor=True))
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:rows=list(pool.map(run,cases))
 (ROOT/'outputs/training-mentorship.json').write_text(json.dumps(dict(version='0.17',scenarios=rows,actual_battles=sum(len(r['battles']) for r in rows)),ensure_ascii=False,indent=2)+'\n');print('MENTOR',len(rows),sum(sum(x['kind']=='mentorship' for x in r['receipts']) for r in rows),flush=True)
