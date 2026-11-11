"""Pure design dialogue selector. Does not implement the Godot runtime."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];F=ROOT/'game/data/final_design'
S=json.loads((F/'character_scripts.json').read_text());SCENES={n['id']:n for n in S['personal']}
def render(nid,choice,presence='healthy',verified=False,event=None,read=True):
 n=SCENES[nid];a=n['actor']
 if presence=='withdrawn':return dict(kind='letter',lines=[n['withdrawn']],choice_applied=False,overlay=None)
 if not read:return dict(kind='unread',lines=[n['unread']],choice_applied=False,overlay=None)
 assert choice in n['choices']
 if choice=='integrated' and not verified:return dict(kind='unmet',lines=[n['unmet']],choice_applied=False,overlay=None)
 opening=n['injured_opening'] if presence=='injured' else n['opening'];replies=n['injured_choices'][choice] if presence=='injured' else n['choices'][choice];overlay=None
 if event and a in event.get('known_by',[]) and (a in [event.get('observer'),event.get('target')] or event.get('responsibility',{}).get(a,0)>0):
  responsibility=event.get('responsibility',{});share=responsibility.get(a,0)
  overlay='unknown' if event.get('evidence')!='verified' or not responsibility else 'self' if share==1 else 'shared' if 0<share<1 else 'other'
 lines=opening+replies+([n['later_breach_'+overlay]] if overlay else [])
 return dict(kind=presence,lines=lines,choice_applied=True,overlay=overlay)
