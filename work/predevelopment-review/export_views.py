"""Export existing canonical domains; never merge historical patches."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[2];F=R/'game/data/final_design'
base=json.loads((F/'release_baseline.json').read_text());manifest=json.loads((F/'design_manifest.json').read_text())
assert base['version']==manifest['version']
for rel,key in manifest['generated_views'].items():
 path=(R/rel).resolve();assert path.is_relative_to((R/'game/data').resolve()) and path.suffix=='.json'
 path.write_text(json.dumps(base['domains'][key],ensure_ascii=False,indent=2)+'\n')
for rel,key,field in [('game/data/equipment.json','equipment','items'),('game/data/enemies.json','enemies',None)]:
 value=base['domains'][key];value=value[field] if field else value
 (R/rel).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print('Exported current baseline views; no runtime changes')
