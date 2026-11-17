"""Offline localization authoring. No credentials or model calls in the game."""
from pathlib import Path
import argparse, concurrent.futures, hashlib, json, os, re, time, urllib.request, urllib.error
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'work/localization-20261117'
CJK=re.compile('[\u4e00-\u9fff]')
TOKENS=re.compile(r'\#[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
def environment():
    conf=dict(os.environ)
    p=ROOT/'.env'
    if p.exists():
        for line in p.read_text().splitlines():
            if '=' in line and not line.lstrip().startswith('#'):
                k,v=line.split('=',1);conf.setdefault(k.strip(),v.strip().strip('\"\''))
    return conf
def extract():
    values=set()
    def walk(v):
        if isinstance(v,str) and CJK.search(v):values.add(v)
        elif isinstance(v,dict):
            for x in v.values():walk(x)
        elif isinstance(v,list):
            for x in v:walk(x)
    for p in [ROOT/'game/data/localization/zh_CN.json',ROOT/'game/data/final_design/release_baseline.json',*(ROOT/'game/data/presentation').glob('*.json')]:walk(json.loads(p.read_text()))
    for p in [*(ROOT/'game/scripts/presentation').glob('*.gd'),*(ROOT/'game/scripts/domain').glob('*.gd'),ROOT/'game/scripts/app/main.gd']:
        if p.name=='localization.gd':continue
        for m in TOKENS.finditer(p.read_text()):
            if m.group().startswith('"'):
                try:walk(json.loads(m.group()))
                except ValueError:pass
    return sorted(values)
def request(payload):
    key=environment().get('aliyun-apikey')
    if not key:raise RuntimeError('Missing configured Aliyun credential')
    req=urllib.request.Request('https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=120) as response:return json.load(response)
    except urllib.error.HTTPError as error:
        try:data=json.loads(error.read());code=data.get('error',{}).get('code',data.get('code','unknown'))
        except Exception:code='unreadable'
        raise RuntimeError(f'Provider HTTP {error.code}, code={code}') from None

def translate_batch(items,language):
    source={str(i):text for i,text in enumerate(items)}
    prompt=('Translate the JSON values for Night Tide Agency, a grounded tactical rescue game in a flooded city. '
    'Return a JSON object with exactly the same keys and no extra commentary. Preserve all printf placeholders '
    '(%s %d %.1f etc), numeric values, literal newlines, identifiers, and markup. Do not add or remove placeholders; '
    'retain their order. Use natural concise game UI wording and nuanced character dialogue. Translate EVERY Chinese word into English for English output; no Chinese characters may remain. Do not invent units or gameplay effects. '
    'Names: 夜潮事务所=Night Tide Agency; 林岚=Lin Lan; 许舟=Xu Zhou; 苏棠=Su Tang; 陈砚=Chen Yan; '
    '叶禾=Ye He; 贺鸣=He Ming; 莫遥=Mo Yao; 江朔=Jiang Shuo. '
    'Translate 行动点 as AP, 稳定 as Stabilize, 交互 as Interact, 交付 as Deliver, 撤出 as Extract, '
    '撤退 as Retreat, 专长 as Specialty. Do not translate code identifiers. Target language: '+language)
    if language=='Traditional Chinese':prompt+=' Keep all character names and game terminology in Chinese; convert to natural Traditional Chinese, not English. The English glossary above is only for English translations.'
    result=request({'model':'qwen-plus','messages':[{'role':'system','content':prompt},{'role':'user','content':json.dumps(source,ensure_ascii=False)}],'response_format':{'type':'json_object'},'temperature':0.2,'enable_thinking':False})
    text=result['choices'][0]['message']['content'];data=json.loads(text)
    if set(data)!=set(source):raise ValueError('Translation keys differ')
    pattern=r'%[-+0#]*\d*(?:\.\d+)?[sdif]|%%'
    for key,value in data.items():
        if not isinstance(value,str) or not value:raise ValueError('Empty translated value')
        if language=='English' and CJK.search(value):raise ValueError('Untranslated Chinese remains')
        if re.findall(pattern,value)!=re.findall(pattern,source[key]):raise ValueError('Placeholders differ')
    return {source[key]:value for key,value in data.items()},result.get('usage',{})
def run(language,limit=0,batch_size=24):
    WORK.mkdir(parents=True,exist_ok=True)
    source=extract();(WORK/'source-strings.json').write_text(json.dumps(source,ensure_ascii=False,indent=2))
    cache=WORK/('translations-'+language+'.json')
    translated=json.loads(cache.read_text()) if cache.exists() else {}
    todo=[s for s in source if s not in translated]
    if limit:todo=todo[:limit]
    batches=[todo[i:i+batch_size] for i in range(0,len(todo),batch_size)]
    failures=[]
    def job(batch):
        for attempt in range(3):
            try:return translate_batch(batch,language)
            except Exception as error:
                if attempt==2:return {'_failed':batch,'_error':str(error)},{}
                time.sleep(2+attempt*2)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for data,usage in pool.map(job,batches):
            if '_failed' in data:failures.append(data)
            else:translated.update(data)
            cache.write_text(json.dumps(translated,ensure_ascii=False,indent=2)+'\n')
            print(f'{language}: {len(translated)}/{len(source)} translated; failed batches {len(failures)}',flush=True)
    (WORK/('failures-'+language+'.json')).write_text(json.dumps(failures,ensure_ascii=False,indent=2))
    return len(failures)
def install():
    overrides=json.loads((ROOT/'tools/localization_overrides.json').read_text())
    source=extract()
    for language,locale in [('English','en'),('Traditional Chinese','zh_TW')]:
        data=json.loads((WORK/('translations-'+language+'.json')).read_text())
        data.update(overrides[locale])
        missing=set(source)-data.keys()
        if missing:raise ValueError(f'{locale}: {len(missing)} untranslated sources')
        if locale=='en':data={s:t.translate(str.maketrans({'’':"'",'‘':"'",'“':'"','”':'"'})) for s,t in data.items()}
        (ROOT/f'game/data/localization/{locale}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def repair_english():
    cache=WORK/'translations-English.json';data=json.loads(cache.read_text())
    overrides=json.loads((ROOT/'tools/localization_overrides.json').read_text())['en'];data.update(overrides)
    todo=[s for s in extract() if s not in data or CJK.search(data[s])]
    failures=[]
    for source in todo:
        try:
            result=request({'model':'qwen-mt-plus','messages':[{'role':'user','content':source}],
                            'translation_options':{'source_lang':'Chinese','target_lang':'English'}})
            translated=result['choices'][0]['message']['content']
            pattern=r'%[-+0#]*\d*(?:\.\d+)?[sdif]|%%'
            if CJK.search(translated) or re.findall(pattern,source)!=re.findall(pattern,translated):raise ValueError('Translation validation failed')
            data[source]=translated
            cache.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
        except Exception as error:failures.append({'source':source,'error_type':type(error).__name__})
    (WORK/'mt-failures.json').write_text(json.dumps(failures,ensure_ascii=False,indent=2)+'\n')
    return len(failures)
if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--language',choices=['English','Traditional Chinese'],default='English')
    parser.add_argument('--limit',type=int,default=0)
    parser.add_argument('--batch-size',type=int,default=24)
    parser.add_argument('--repair-english',action='store_true')
    parser.add_argument('--install',action='store_true',help='Install cached translations and reviewed overrides; no API calls')
    args=parser.parse_args()
    if args.install:install()
    else:raise SystemExit(repair_english() if args.repair_english else run(args.language,args.limit,args.batch_size))
