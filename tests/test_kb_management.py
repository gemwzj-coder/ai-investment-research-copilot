import tempfile
import unittest
from pathlib import Path

import kb_management as kbm


class KnowledgeManagementTests(unittest.TestCase):
    def test_file_sha256_is_stable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "knowledge.txt"
            path.write_text("Q: test\nA: answer\n", encoding="utf-8")
            first_hash = kbm.file_sha256(str(path))
            path.write_text("Q: changed\nA: answer\n", encoding="utf-8")

            self.assertNotEqual(first_hash, kbm.file_sha256(str(path)))

    def test_validation_detects_duplicate_questions(self):
        content = """数据截止 2026-08-14

Q: 示例问题
A: 示例回答

Q: 示例问题
A: 重复回答
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "knowledge.txt"
            path.write_text(content, encoding="utf-8")
            report = kbm.validate_knowledge(str(path))

        issue_types = {issue["type"] for issue in report["issues"]}
        self.assertIn("duplicate_question", issue_types)

    def test_source_fingerprint_changes_when_manifest_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            knowledge = Path(directory) / "knowledge.txt"
            manifest = Path(directory) / "source_manifest.json"
            knowledge.write_text("Q: test\nA: answer\n", encoding="utf-8")
            manifest.write_text('{"sources": []}', encoding="utf-8")
            first = kbm.source_fingerprint(str(knowledge), str(manifest))
            manifest.write_text('{"sources": [{"id": "new"}]}', encoding="utf-8")

            self.assertNotEqual(first, kbm.source_fingerprint(str(knowledge), str(manifest)))


if __name__ == "__main__":
    unittest.main()
