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
if __name__=='__main__':unittest.main()
