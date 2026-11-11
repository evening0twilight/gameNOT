from model import *
rows=[]
for b in B.values():
 for route,groups in b.get('route_groups',{'default':b['mandatory_groups']}).items():
  for goals in itertools.product(*groups):
   for dock in [False,True]:
    p=['lin','xu','su'];rs=[]
    for plan in configurations(b,goals):
     _,r=play(b,goals,p,3,plan,False,dock=dock);rs.append(r)
    r=min(rs,key=rank);rows.append(dict(mission=b['id'],route=route,goals=goals,dock=dock,success=r['success'],rounds=r['rounds'],damage=r['damage'],secured=r['secured']))
(ROOT/'outputs/growth-identity-ports.json').write_text(json.dumps(dict(scope='46goal variants at both physical exits using level3initial trio/no specialties. Alternate dock is geometrically tested on all36maps but earned availability remains late main missions only. Existing vehicle destinations and deadlines unchanged.',rows=rows),ensure_ascii=False,indent=2)+'\n');print('PORTS',len(rows),sum(r['success'] for r in rows))
