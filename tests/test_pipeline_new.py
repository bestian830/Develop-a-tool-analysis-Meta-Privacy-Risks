import unittest
import json
import shutil
from pathlib import Path
from src.parser import html_to_sections
from src.clause_splitter import split_into_clauses
from src.tagger import run_tagging
from src.differ import diff_versions

class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("tests/temp_data")
        self.test_dir.mkdir(exist_ok=True)
        
        # Create dummy HTML
        self.html_path = self.test_dir / "test_policy.html"
        self.html_path.write_text("""
        <html>
            <body>
                <h1>Information we collect</h1>
                <p>When you use the Ray-Ban Meta smart glasses to take photos, we collect audio and visual information.</p>
                <p>We also collect device information such as battery level.</p>
                <h2>How we use information</h2>
                <p>We use information to improve our services.</p>
            </body>
        </html>
        """, encoding="utf-8")
        
        self.product = "test_product"
        self.doc_id = "test_v1"

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_full_flow(self):
        # 1. Parse
        clean_path = self.test_dir / "clean.json"
        html_to_sections(self.html_path, clean_path)
        self.assertTrue(clean_path.exists())
        sections = json.loads(clean_path.read_text())
        self.assertEqual(len(sections), 3)
        self.assertEqual(sections[0]["section"], "Information we collect")

        # 2. Split
        clauses_path = self.test_dir / "clauses.json"
        split_into_clauses(clean_path, clauses_path)
        self.assertTrue(clauses_path.exists())
        clauses = json.loads(clauses_path.read_text())
        # Should be at least 3 clauses (one per sentence)
        self.assertTrue(len(clauses) >= 3)

        # 3. Tag
        claims_path = self.test_dir / "claims.json"
        run_tagging(clauses_path, self.product, self.doc_id, claims_path)
        self.assertTrue(claims_path.exists())
        claims = json.loads(claims_path.read_text())
        
        # Check if we found the photo taking claim
        found_photo = False
        for c in claims:
            if "take_photo_with_glasses" in c["activity"] and "video_image" in c["data_collected"]:
                found_photo = True
                break
        self.assertTrue(found_photo, "Failed to identify photo taking activity and data")

    def test_diff(self):
        # Create two claim files
        claims1 = [
            {
                "doc_id": "v1", "product": "p", "section": "S1", "clause_id": 1,
                "activity": ["act1"], "data_collected": ["data1"], "source_text": "text1"
            }
        ]
        claims2 = [
            {
                "doc_id": "v2", "product": "p", "section": "S1", "clause_id": 1,
                "activity": ["act1"], "data_collected": ["data1"], "source_text": "text1"
            },
            {
                "doc_id": "v2", "product": "p", "section": "S1", "clause_id": 2,
                "activity": ["act2"], "data_collected": ["data2"], "source_text": "text2"
            }
        ]
        
        p1 = self.test_dir / "claims1.json"
        p2 = self.test_dir / "claims2.json"
        p1.write_text(json.dumps(claims1))
        p2.write_text(json.dumps(claims2))
        
        diff_out = self.test_dir / "diff.json"
        result = diff_versions(p1, p2, diff_out)
        
        self.assertEqual(result["added_count"], 1)
        self.assertEqual(result["kept_count"], 1)
        self.assertEqual(result["removed_count"], 0)

if __name__ == "__main__":
    unittest.main()
