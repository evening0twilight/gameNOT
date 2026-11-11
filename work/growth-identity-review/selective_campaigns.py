from campaign_review import *
if __name__=='__main__':
 cases=[('仅为下一次出勤临界解锁带教',dict(training='selective',formation='flex',pacts=True),dict(sides=True)),('同样培养：只在M22选择东侧接应',dict(training='selective',formation='flex',pacts=True,dock=True,dock_days=[22]),dict(sides=True))]
 with ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('fork')) as pool:rows=list(pool.map(one,cases))
 for s in rows:print(s['summary']['name'],s['summary']['positive_relationships'],s['summary']['resources'],sum(b['rounds'] for b in s['battles']),sum(b['damage'] for b in s['battles']),flush=True)
 (ROOT/'outputs/growth-identity-selective-campaigns.json').write_text(json.dumps(dict(scope='Two preselected campaign preferences: mentorship only bridges a next-day deployment skill threshold beyond ordinary3XP; docking is deliberately chosen for M22. Not a universal optimal policy.',scenarios=rows),ensure_ascii=False,indent=2)+'\n')
