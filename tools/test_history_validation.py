"""Portability must never turn missing/changed design evidence into a pass."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import check_product018 as check

class HistoryValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/'docs').mkdir()
        self.patch=patch.object(check,'ROOT',self.root);self.patch.start();self.addCleanup(self.patch.stop)
        self.hashes={}
        for name in ['build/old.zip','outputs/p4-feedback-runtime.avi','game/data/final_design/release_baseline.json']:
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'original')
            self.hashes[name]=hashlib.sha256(b'original').hexdigest()
        for index,name in enumerate(['baseline018-preserved.json','p4-preserved-files.json','p4-feedback-preserved.json','p4-tuning-preserved.json']):
            (self.root/'docs'/name).write_text(json.dumps(self.hashes if index==0 else {}))
        self.write_retirements()
    def write_retirements(self,discarded=None,duplicates=None):
        (self.root/check.RETIREMENTS).write_text(json.dumps({'discarded':discarded or {},'duplicate_captures':duplicates or {}}))
    def test_complete_default(self):
        self.assertEqual(check.preserved(),3);self.assertTrue(check.history_status()['complete'])
    def test_missing_fails_by_default(self):
        (self.root/'build/old.zip').unlink()
        with self.assertRaises(SystemExit):check.history_status()
    def test_excluded_history_is_explicitly_reported(self):
        (self.root/'build/old.zip').unlink();(self.root/'outputs/p4-feedback-runtime.avi').unlink()
        result=check.history_status(True)
        self.assertEqual(result['verified'],1);self.assertEqual(len(result['missing']),2);self.assertFalse(result['complete'])
    def test_missing_design_never_allowed(self):
        (self.root/'game/data/final_design/release_baseline.json').unlink()
        with self.assertRaises(SystemExit):check.history_status(True)
    def test_changed_archive_never_allowed(self):
        (self.root/'build/old.zip').write_bytes(b'changed')
        with self.assertRaises(SystemExit):check.history_status(True)
    def test_changed_design_never_allowed(self):
        (self.root/'game/data/final_design/release_baseline.json').write_bytes(b'changed')
        with self.assertRaises(SystemExit):check.history_status(True)
    def test_recorded_retirement_is_distinct_from_unavailable(self):
        name='build/old.zip'
        self.write_retirements(discarded={name:self.hashes[name]})
        (self.root/name).unlink()
        result=check.history_status()
        self.assertEqual(result,{'verified':2,'expected':3,'missing':[],'retired':[name],'complete':False})
        (self.root/name).write_bytes(b'changed')
        with self.assertRaisesRegex(SystemExit,'Historical artifact changed'):check.history_status(True)
        (self.root/name).write_bytes(b'original')
        self.assertTrue(check.history_status()['complete'])
    def test_protected_capture_keeps_its_hash_check_via_retained_copy(self):
        removed='outputs/p4-feedback-gui/M01-start.png'
        kept='outputs/p4-tuning-gui/M01-start.png'
        for name in [removed,kept]:
            self.hashes[name]=hashlib.sha256(b'capture').hexdigest()
        (self.root/'docs/baseline018-preserved.json').write_text(json.dumps(self.hashes))
        self.write_retirements(duplicates={removed:kept})
        (self.root/kept).parent.mkdir()
        (self.root/kept).write_bytes(b'capture')
        self.assertEqual(check.history_status()['retired'],[removed])
        (self.root/kept).write_bytes(b'changed')
        with self.assertRaisesRegex(SystemExit,'Historical artifact changed'):check.history_status(True)
        (self.root/kept).unlink()
        with self.assertRaisesRegex(SystemExit,'Historical artifact missing'):check.history_status(True)
    def test_design_cannot_be_retired(self):
        name='game/data/final_design/release_baseline.json'
        self.write_retirements(discarded={name:self.hashes[name]})
        with self.assertRaisesRegex(SystemExit,'Invalid historical artifact retirement'):check.history_status()
    def prepare_amendment(self):
        fields=['schedule','not_railroad','automatic_budget']
        experience={'tutorial_policy':dict.fromkeys(fields,'old'),'other':'frozen'}
        records={}
        for leaf,before in [('release_baseline.json',{'domains':{'experience':experience},'combat':'frozen'}),('player_experience_contract.json',experience)]:
            name='game/data/final_design/'+leaf
            current=self.root/name;current.write_text(json.dumps(before))
            old=check.digest(current)
            if name in self.hashes:self.hashes[name]=old
            archive='docs/p4-firstshift-20261117/before-'+leaf
            target=self.root/archive;target.parent.mkdir(exist_ok=True);target.write_bytes(current.read_bytes())
            after=json.loads(current.read_text());domain=after['domains']['experience'] if 'domains' in after else after
            for field in fields:domain['tutorial_policy'][field]='user-requested'
            current.write_text(json.dumps(after))
            records[name]={'archive':archive,'before_sha256':old,'after_sha256':check.digest(current)}
        (self.root/'docs/baseline018-preserved.json').write_text(json.dumps(self.hashes))
        (self.root/check.TUTORIAL_AMENDMENT).write_text(json.dumps({'paths':records,'changed_fields':fields}))
        return records
    def test_tutorial_amendment_preserves_original_at_archive(self):
        self.prepare_amendment();result=check.history_status()
        self.assertEqual(result['verified'],3);self.assertEqual(result['unchanged_original_paths'],2)
        self.assertEqual(len(result['amended_originals_verified_at']),1)
    def test_missing_amended_original_is_not_permitted(self):
        records=self.prepare_amendment()
        (self.root/records['game/data/final_design/release_baseline.json']['archive']).unlink()
        with self.assertRaisesRegex(SystemExit,'Missing tutorial amendment evidence'):check.history_status(True)
    def test_tutorial_amendment_cannot_change_gameplay_even_with_updated_hash(self):
        records=self.prepare_amendment();name='game/data/final_design/release_baseline.json'
        path=self.root/name;data=json.loads(path.read_text());data['combat']='modified';path.write_text(json.dumps(data))
        decision=json.loads((self.root/check.TUTORIAL_AMENDMENT).read_text());decision['paths'][name]['after_sha256']=check.digest(path)
        (self.root/check.TUTORIAL_AMENDMENT).write_text(json.dumps(decision))
        with self.assertRaisesRegex(SystemExit,'changed unrelated design'):check.history_status()
if __name__=='__main__':unittest.main()
