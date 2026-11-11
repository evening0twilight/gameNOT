import json,urllib.request
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from bs4 import BeautifulSoup
root=Path(__file__).parent
base=json.loads((root/'corpus.json').read_text())
games={x['appid']:(x['group'],x['name']) for x in base}
games.update({699330:('C','The Iron Oath'),280320:('C','Adventurer Manager'),1669980:('B-boundary','Volcano Princess'),1948980:('A-boundary',"Hero's Adventure")})
def fetch(j):
 a,g,n,cc,lang=j;url=f'https://store.steampowered.com/app/{a}/?cc={cc}&l={lang}'
 r={'appid':a,'group':g,'name':n,'region':cc,'lang':lang,'url':url}
 try:
  raw=urllib.request.urlopen(url,timeout=35).read().decode();(root/f'{a}-{cc}.html').write_text(raw)
  s=BeautifulSoup(raw,'html.parser')
  r['title']=s.title.get_text()
  r['review_rows']=[x.get_text(' ',strip=True) for x in s.select('.user_reviews_summary_row')][:2]
  r['purchases']=[x.get_text(' ',strip=True) for x in s.select('.game_area_purchase_game')][:2]
  r['release']=s.select_one('.release_date').get_text(' ',strip=True) if s.select_one('.release_date') else ''
  r['language_table']=s.select_one('.game_language_options').get_text(' ',strip=True) if s.select_one('.game_language_options') else ''
 except Exception as e:r['error']=str(e)
 return r
jobs=[(a,g,n,cc,lang) for a,(g,n) in games.items() for cc,lang in [('us','english'),('cn','schinese')]]
results=[]
with ThreadPoolExecutor(max_workers=4) as ex:
 for f in as_completed([ex.submit(fetch,j) for j in jobs]):
  r=f.result();results.append(r);print(r['appid'],r['region'],r.get('error','ok'),flush=True)
(root/'markets.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
