"""Generate an explicitly requested instrumental audition; never change production audio automatically."""
from pathlib import Path
import argparse,json,urllib.request,urllib.error,hashlib,time
from localize_product018 import environment
ROOT=Path(__file__).resolve().parents[1]
def main(workspace,only_model=""):
    import http.client
    conf=environment();workspace=workspace or conf.get('SFM_WORKSPACE_ID','')
    if not workspace:raise SystemExit('Missing workspace ID')
    import re
    if not re.fullmatch('[a-zA-Z0-9-]+',workspace):raise SystemExit('Invalid workspace identifier')
    output=ROOT/'outputs/aliyun-audio-20261117';output.mkdir(parents=True,exist_ok=True)
    prompt='原创游戏配乐，无人声、无演唱、无说话。洪水后的城市救援事务所，第一晚营地，窗外细雨、室内一盏暖灯。克制温暖而略有忧伤，疲惫后的安定感；稀疏的柔音钢琴、温暖低音弦乐、轻微空气质感，72 BPM，避免激昂、避免流行歌曲结构、避免强烈鼓点。约45秒，稳定织体，适合循环作背景，不要大起大落，不要模拟任何现有歌曲。'
    report_path=output/'probe.json'
    reports=json.loads(report_path.read_text()) if report_path.exists() else []
    for model,path,body in [('fun-music-v1','audio/music/generation',{'prompt':prompt,'is_instrumental':True,'format':'wav'}),('qwen-audio-3.1-tts-next','audio/tts/SpeechSynthesizer',{'text_prompt':prompt,'format':'wav','sample_rate':48000,'channels':2})]:
        if only_model and model!=only_model:continue
        stage='generation'
        payload={'model':model,'input':body};record={'model':model,'prompt':prompt,'instrumental_requested':True,'status':'pending'}
        url=f'https://{workspace}.cn-beijing.maas.aliyuncs.com/api/v1/services/{path}'
        try:
            req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+conf['aliyun-apikey'],'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=300) as response:
                try:raw=response.read()
                except http.client.IncompleteRead as error:raw=error.partial
                data=json.loads(raw)
            cache=ROOT/'work/aliyun-audio-20261117';cache.mkdir(parents=True,exist_ok=True)
            (cache/(model+'-response.json')).write_text(json.dumps(data))
            stage='download'
            audio_url=data.get('output',{}).get('audio',{}).get('url')
            if not audio_url:record.update(status='no_audio',provider_code=data.get('code','unknown'))
            else:
                audio_url=audio_url.replace('http://','https://',1)
                with urllib.request.urlopen(audio_url,timeout=120) as response:audio=response.read()
                filename=output/(model+'-camp.wav');filename.write_bytes(audio)
                record.update(status='generated',file=str(filename.relative_to(ROOT)),sha256=hashlib.sha256(audio).hexdigest(),usage=data.get('usage',{}),request_id=data.get('request_id',''))
        except urllib.error.HTTPError as error:
            try:data=json.loads(error.read());code=data.get('code',data.get('error',{}).get('code','unknown'))
            except Exception:code='unreadable'
            record.update(status='rejected',http_status=error.code,provider_code=code)
        except Exception as error:record.update(status='connection_error',stage=stage,exception_type=type(error).__name__)
        reports.append(record)
        (output/'probe.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
        print(model,record['status'],record.get('provider_code',''),flush=True)
        if record['status']=='generated':break
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--workspace',default='');parser.add_argument('--model',default='');args=parser.parse_args();main(args.workspace,args.model)
