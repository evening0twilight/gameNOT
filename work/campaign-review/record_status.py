from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
def update(file,values):
 p=ROOT/file;d=json.loads(p.read_text());d.update(values);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
update('game/docs/development.json',{'design_version':'0.7-tactical-review','project_stage':'Design refinement only; user explicitly deferred formal development. Existing Godot runtime remains a foundation.','formal_development_gate':'Do not begin formal implementation under the latest instruction; finish design review first.','latest_review':'../../outputs/tactical-playability-review.html','logical_closure_status':'ALL_36_MAPS_HAVE_BOUNDED_TACTICAL_WITNESSES; EXHAUSTIVE_COMBINATIONS_AND_HUMAN_PLAYABILITY_NOT_CLAIMED'})
update('game/data/product.json',{'design_version':'0.7-tactical-review','implementation_status':'按用户最新指示继续完善方案；暂不进入正式开发。已有Godot基础工程未接入整局运行系统。'})
update('game/docs/logic-audit.json',{'current_revision':'0.7-tactical-review','whole_campaign_contract':'data/final_design/whole_campaign_contract.json','latest_resolutions':['Separate epilogue career from relationship overlays','Separate protocol learning from situational field permissions','Explicit target tags, flood sources and post-unlock fire encounters','Single settlement source for money, XP, world, injuries and contributions','Preserve crafted/packed/consumed/returned inventory conservation'],'formal_development':'deferred_by_user'})
print('Recorded design-only phase; no runtime implementation authorized in this stage.')
