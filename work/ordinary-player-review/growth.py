from campaigns import *

def growth_cases():
 for who,behavior,training in itertools.product(['chen','ye','he','mo','jiang'],['cautious','favorite'],['none','targeted','favorite']):
  yield dict(name=f'{who}/{behavior}/{training}',behavior=behavior,difficulty='standard',variant='A',ending='evacuation',choice_index=0,sides='some',favorites=[who,'lin','xu'],formation='favorite',training=training,training_actor=who,shop=False,pack=1,treat=True)
if __name__=='__main__':
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:rows=list(pool.map(run,growth_cases()))
 (ROOT/'outputs/ordinary-player-growth.json').write_text(json.dumps(dict(version='0.16',scenarios=rows,actual_battles=sum(len(r['battles']) for r in rows),scope='30paired earned-state campaigns:5latercharacters x2committedordinarypolicies xnone/threshold/nightlytraining. Training costs, fatigue and actual deployment retained; no freeL5.'),ensure_ascii=False,indent=2)+'\n');print('GROWTH',len(rows),sum(len(r['battles']) for r in rows),flush=True)
