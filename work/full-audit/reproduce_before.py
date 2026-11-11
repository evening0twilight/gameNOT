"""Reproduce three recorded defects from the preserved0.13 adapter only.
Does not roll back design data or production files. Lower-level action code used
by these cases is unchanged; the current adapter is never imported here.
"""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work/growth-identity-review'))
snapshot=ROOT/'work/full-audit/before/work/growth-identity-review/model.py'
ns={'__file__':str(ROOT/'work/growth-identity-review/model.py'),'__name__':'preserved_identity_adapter'}
exec(compile(snapshot.read_text(),str(snapshot),'exec'),ns)
ns['R']=ROOT
source=(ROOT/'work/full-audit/probe.py').read_text();source=source[source.index('def fixture('):]
exec(compile(source,'preserved_adapter_probes','exec'),ns)
assert all(r['bug'] for r in ns['out'])
