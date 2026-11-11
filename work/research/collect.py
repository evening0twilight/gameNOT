import urllib.request, json, re, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

root=Path(__file__).parent
games=[
 ('A',763890,'Wildermyth'),('A',365360,'Battle Brothers'),('A',1940340,'Darkest Dungeon II'),('A',601840,'Griftlands'),
 ('B',1148760,'I Was a Teenage Exocolonist'),('B',1340480,'The Cosmic Wheel Sisterhood'),('B',1266030,'The Pale Beyond'),('B',462770,'Pyre'),
 ('C',2026000,'Our Adventurer Guild'),('C',1043260,'Gladiator Guild Manager'),('C',1119600,'Help Will Come Tomorrow'),('C',317820,'Guild of Dungeoneering')]
core=[763890,601840,1148760,1266030,2026000,1119600]

def fetch(job):
 group,appid,name,kind,url=job
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=35) as r: raw=r.read().decode('utf-8','replace')
  (root/f'{appid}-{kind}.html').write_text(raw)
  s=BeautifulSoup(raw,'html.parser')
  result={'group':group,'appid':appid,'name':name,'kind':kind,'url':url}
  if kind=='store':
   result['title']=s.title.get_text() if s.title else ''
   result['review_rows']=[x.get_text(' ',strip=True) for x in s.select('.user_reviews_summary_row')]
   result['review_tooltips']=[x.get('data-tooltip-html') for x in s.select('.user_reviews_summary_row')]
   result['release']=s.select_one('.release_date').get_text(' ',strip=True) if s.select_one('.release_date') else ''
   result['prices']=[x.get_text(' ',strip=True) for x in s.select('.game_purchase_price, .discount_original_price, .discount_final_price')][:9]
   result['description']=s.select_one('#game_area_description').get_text(' ',strip=True) if s.select_one('#game_area_description') else ''
   result['language_table']=s.select_one('.game_language_options').get_text(' ',strip=True) if s.select_one('.game_language_options') else ''
  else:
   result['reviews']=[]
   for c in s.select('.apphub_Card')[:5]:
    text=c.select_one('.apphub_CardTextContent')
    if not text: continue
    date=text.select_one('.date_posted')
    date_text=date.get_text(' ',strip=True) if date else ''
    if date:date.extract()
    get=lambda selector:c.select_one(selector).get_text(' ',strip=True) if c.select_one(selector) else ''
    result['reviews'].append({'url':c.get('data-modal-content-url'),'date':date_text,'recommendation':get('.title'),'hours':get('.hours'),'text':text.get_text(' ',strip=True)})
  return result
 except Exception as e:return {'group':group,'appid':appid,'name':name,'kind':kind,'url':url,'error':str(e)}

jobs=[]
for g,a,n in games:
 jobs.append((g,a,n,'store',f'https://store.steampowered.com/app/{a}/'))
 jobs.append((g,a,n,'helpful',f'https://steamcommunity.com/app/{a}/reviews/?browsefilter=toprated'))
 jobs.append((g,a,n,'negative',f'https://steamcommunity.com/app/{a}/negativereviews/?browsefilter=toprated'))
 if a in core:
  jobs.append((g,a,n,'recent',f'https://steamcommunity.com/app/{a}/reviews/?browsefilter=mostrecent'))
  jobs.append((g,a,n,'chinese',f'https://steamcommunity.com/app/{a}/reviews/?browsefilter=toprated&filterLanguage=schinese'))
results=[]
with ThreadPoolExecutor(max_workers=4) as ex:
 for future in as_completed([ex.submit(fetch,j) for j in jobs]):
  r=future.result();results.append(r)
  print(r['appid'],r['kind'],len(r.get('reviews',[])),r.get('error',''),flush=True)
(root/'corpus.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
unique={r['url']:r for p in results for r in p.get('reviews',[]) if r.get('url')}
print('DONE',len(results),'pages',len(unique),'unique reviews')
