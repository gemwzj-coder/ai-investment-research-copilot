import json
import tempfile
import unittest
from pathlib import Path

import source_registry as registry


def demo_source(file_name="knowledge.txt"):
    return {
        "id": "demo-1", "title": "脱敏资料", "source_type": "wiki_export",
        "source_url": "demo://source", "owner": "投研运营", "updated_at": "2026-08-14",
        "data_as_of": "2026-08-14", "access_level": "internal_demo",
        "version": "v1", "file": file_name,
    }


class SourceRegistryTests(unittest.TestCase):
    def test_matches_source_by_knowledge_file_name(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "source_manifest.json"
            manifest.write_text(json.dumps({"sources": [demo_source()]}, ensure_ascii=False), encoding="utf-8")
            source = registry.source_for_file("nested/knowledge.txt", str(manifest))

        self.assertEqual(source["id"], "demo-1")
        self.assertIn("数据截至=2026-08-14", registry.provenance_line(source))

    def test_rejects_source_missing_required_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "source_manifest.json"
            manifest.write_text(json.dumps({"sources": [{"id": "broken"}]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                registry.load_manifest(str(manifest))


if __name__ == "__main__":
    unittest.main()
