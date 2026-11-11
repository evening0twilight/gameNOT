"""Rebuild design artifacts and checks only; formal game development remains on hold."""
from pathlib import Path
import runpy,sys
HERE=Path(__file__).resolve().parent;REVIEW=HERE.parent/'campaign-review'
for name in ['build_systems.py','build_boards.py','build_stories.py','build_integration.py']:
 runpy.run_path(str(HERE/name),run_name='__main__')
runpy.run_path(str(HERE.parent/'relationship-review/clarify.py'),run_name='__main__')
for name in ['build_contract.py','apply_design_revisions.py']:
 runpy.run_path(str(REVIEW/name),run_name='__main__')
runpy.run_path(str(HERE.parent/'system-audit/apply_design.py'),run_name='__main__')
runpy.run_path(str(HERE.parent/'tactical-review/apply_design.py'),run_name='__main__')
runpy.run_path(str(HERE.parent/'player-experience/build_design.py'),run_name='__main__')
runpy.run_path(str(HERE.parent/'integrated-review/apply_design.py'),run_name='__main__')
runpy.run_path(str(HERE.parent/'approach-review/apply_design.py'),run_name='__main__')
for name in ['validate.py','combat_example.py','verify_contracts.py','sync_legacy.py']:
 runpy.run_path(str(HERE/name),run_name='__main__')
for name in ['ledger_review.py','check_targets.py','build_review.py','record_status.py']:
 runpy.run_path(str(REVIEW/name),run_name='__main__')
for name in ['verify.py','build_report.py']:
 runpy.run_path(str(HERE.parent/'system-audit'/name),run_name='__main__')
sys.path.insert(0,str(HERE.parent/'tactical-review'))
for name in ['mechanic_checks.py','run_matrix.py','replay_checks.py','campaign_from_combat.py','personal_witness.py','build_report.py']:
 runpy.run_path(str(HERE.parent/'tactical-review'/name),run_name='__main__')
for name in ['verify.py','build_report.py']:
 runpy.run_path(str(HERE.parent/'player-experience'/name),run_name='__main__')
sys.path.insert(0,str(HERE.parent/'integrated-review'))
for name in ['run_matrix.py','campaign.py','verify.py','build_report.py']:
 runpy.run_path(str(HERE.parent/'integrated-review'/name),run_name='__main__')
sys.path.insert(0,str(HERE.parent/'approach-review'))
for name in ['run_matrix.py','campaign.py','protocol_witnesses.py','verify.py','build_report.py']:
 runpy.run_path(str(HERE.parent/'approach-review'/name),run_name='__main__')
runpy.run_path(str(HERE/'build_report.py'),run_name='__main__')
runpy.run_path(str(HERE.parent/'tactical-review/final_checks.py'),run_name='__main__')

# Latest player-choice revision is applied after historical0.10 checks.
runpy.run_path(str(HERE.parent/'player-choice-review/rebuild.py'),run_name='__main__')

# Current0.12 investment audit and reduced production scope, after0.11 evidence.
runpy.run_path(str(HERE.parent/'cooperation-value-review/rebuild.py'),run_name='__main__')

#0.13 battle form and growth identity audit on the current reduced scope.
runpy.run_path(str(HERE.parent/'growth-identity-review/rebuild.py'),run_name='__main__')

#0.14 cross-system design audit, after the0.13 baseline.
runpy.run_path(str(HERE.parent/'full-audit/rebuild.py'),run_name='__main__')
