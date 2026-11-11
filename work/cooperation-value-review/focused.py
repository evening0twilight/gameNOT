from routes import *
rows=[]
for mid in ['M06','M08']:
 b=B[mid];goals=[x[0] for x in b['mandatory_groups']]
 for party in itertools.combinations(['lin','xu','su','chen'],3):
  rs=[]
  for plan in configurations(b,goals,True):
   for skills in [False,True]:
    g,r=execute(b,goals,party,{a:2 for a in party},plan,skills=skills,trained=[]);rs.append(r)
  r=min(rs,key=rank);rows.append(compact(r)|{'log':r['log']})
(ROOT/'outputs/cooperation-focused-ordinary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
